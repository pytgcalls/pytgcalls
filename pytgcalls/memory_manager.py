import asyncio
import gc
import logging
from typing import Optional

# Try to import psutil, provide fallback if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

py_logger = logging.getLogger('pytgcalls')


class MemoryManager:
    """Memory manager for PyTgCalls to prevent memory leaks"""

    def __init__(self, pytgcalls_instance, cleanup_interval: int = 300):
        """
        Initialize memory manager

        Args:
            pytgcalls_instance: PyTgCalls instance to manage
            cleanup_interval: Interval in seconds for automatic cleanup
        """
        self.pytgcalls = pytgcalls_instance
        self.cleanup_interval = cleanup_interval
        self._cleanup_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._start_lock = asyncio.Lock()
        self._initial_memory = self.get_memory_usage()

    def get_memory_usage(self) -> dict:
        """Get current memory usage statistics"""
        if not PSUTIL_AVAILABLE:
            return {
                'rss_mb': 0.0,
                'vms_mb': 0.0,
                'percent': 0.0,
                'available_mb': 0.0,
            }

        try:
            process = psutil.Process()
            memory_info = process.memory_info()

            # Metrics are returned in megabytes
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': process.memory_percent(),
                'available_mb': (
                    psutil.virtual_memory().available / 1024 / 1024
                ),
            }
        except Exception as e:
            py_logger.warning(
                'Failed to get memory usage: %s',
                str(e),
            )
            return {
                'rss_mb': 0.0,
                'vms_mb': 0.0,
                'percent': 0.0,
                'available_mb': 0.0,
            }

    def get_memory_increase(self) -> dict:
        """Get memory increase since initialization"""
        current = self.get_memory_usage()
        return {
            'rss_increase_mb': (
                current['rss_mb'] - self._initial_memory['rss_mb']
            ),
            'vms_increase_mb': (
                current['vms_mb'] - self._initial_memory['vms_mb']
            ),
            'percent_increase': (
                current['percent'] - self._initial_memory['percent']
            ),
        }

    async def cleanup_caches(self) -> dict:
        """Cleanup all caches and return statistics"""
        stats = {}

        # Cleanup main caches
        if hasattr(self.pytgcalls, '_cache_user_peer'):
            before_size = self.pytgcalls._cache_user_peer.size()
            cleaned = self.pytgcalls._cache_user_peer.cleanup_expired()
            stats['user_peer_cache'] = {
                'before_size': before_size,
                'cleaned': cleaned,
                'after_size': self.pytgcalls._cache_user_peer.size(),
            }

        # Cleanup client cache
        if hasattr(self.pytgcalls, '_app') and hasattr(
            self.pytgcalls._app,
            '_cache',
        ):
            cleaned = self.pytgcalls._app._cache.cleanup_expired()
            cache_stats = self.pytgcalls._app._cache.get_cache_stats()
            stats['client_cache'] = {
                'cleaned': cleaned,
                'stats': cache_stats,
            }

        # Force garbage collection
        collected = gc.collect()
        stats['garbage_collection'] = {
            'collected_objects': collected,
        }

        return stats

    async def log_memory_stats(self):
        """Log current memory statistics"""
        memory = self.get_memory_usage()
        increase = self.get_memory_increase()

        py_logger.info(
            (
                f"Memory Usage - RSS: {memory['rss_mb']:.1f}MB, "
                f"VMS: {memory['vms_mb']:.1f}MB, "
                f"Percent: {memory['percent']:.1f}%, "
                f"Available: {memory['available_mb']:.1f}MB"
            ),
        )

        if increase['rss_increase_mb'] > 10:  # Log if increase > 10MB
            py_logger.warning(
                (
                    'Memory increase detected - '
                    f"RSS: +{increase['rss_increase_mb']:.1f}MB, "
                    f"VMS: +{increase['vms_increase_mb']:.1f}MB"
                ),
            )

    async def _cleanup_loop(self):
        """Main cleanup loop"""
        while self._is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)

                # Log memory stats
                await self.log_memory_stats()

                # Perform cleanup
                cleanup_stats = await self.cleanup_caches()

                # Check if any cleanup was performed
                user_peer_cleaned = cleanup_stats.get(
                    'user_peer_cache', {},
                ).get('cleaned', 0)
                client_cache_cleaned = cleanup_stats.get(
                    'client_cache', {},
                ).get('cleaned', 0)

                if user_peer_cleaned > 0 or client_cache_cleaned > 0:
                    py_logger.info(f"Cleanup performed: {cleanup_stats}")

            except asyncio.CancelledError:
                # Task was cancelled, exit gracefully
                py_logger.info('Memory manager cleanup loop cancelled')
                break
            except Exception as e:
                py_logger.error(f"Error in cleanup loop: {e}")
                # Add delay after error to prevent infinite error loop
                try:
                    await asyncio.sleep(60)  # Wait 1 minute before retrying
                except asyncio.CancelledError:
                    break

    async def start(self):
        """Start the memory manager"""
        async with self._start_lock:
            if not self._is_running:
                self._is_running = True
                self._cleanup_task = asyncio.create_task(self._cleanup_loop())
                py_logger.info('Memory manager started')

    def stop(self):
        """Stop the memory manager"""
        if self._is_running:
            self._is_running = False
            if self._cleanup_task:
                self._cleanup_task.cancel()
            py_logger.info('Memory manager stopped')

    async def force_cleanup(self) -> dict:
        """Force immediate cleanup and return statistics"""
        stats = await self.cleanup_caches()
        await self.log_memory_stats()
        return stats
