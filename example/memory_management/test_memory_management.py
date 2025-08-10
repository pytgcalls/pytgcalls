#!/usr/bin/env python3
"""
Memory Management Test Script for PyTgCalls

This script demonstrates the memory management improvements and helps
identify potential memory leaks.
"""
import asyncio
import logging
import time
import tracemalloc
from typing import Any
from typing import Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)


class MemoryTest:
    """Test class for memory management features"""

    def __init__(self):
        self.test_results = {}

    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage using tracemalloc"""
        current, peak = tracemalloc.get_traced_memory()
        return {
            'current_mb': current / 1024 / 1024,
            'peak_mb': peak / 1024 / 1024,
        }

    def log_memory_usage(self, stage: str):
        """Log memory usage at a specific stage"""
        memory = self.get_memory_usage()
        logger.info(
            (
                f"[{stage}] Memory: {memory['current_mb']:.2f}MB "
                f"(Peak: {memory['peak_mb']:.2f}MB)"
            ),
        )
        return memory

    async def test_cache_operations(self, call_py) -> Dict[str, Any]:
        """Test cache operations and memory usage"""
        logger.info('Testing cache operations...')

        # Initial memory
        initial_memory = self.log_memory_usage('Cache Test Start')

        # Simulate cache operations
        for i in range(1000):
            # Create temporary data
            temp_data = {
                f'key_{i}': f'value_{i}' * 100,
                'timestamp': time.time(),
                'index': i,
                'nested': {
                    'data': [j for j in range(10)],
                    'metadata': {'test': True},
                },
            }

            # Add to cache
            call_py._cache_user_peer.put(i, temp_data)

            if i % 100 == 0:
                await asyncio.sleep(0.01)  # Small delay

        # Memory after cache operations
        after_cache_memory = self.log_memory_usage('After Cache Operations')

        # Force cleanup
        cleanup_stats = await call_py.force_cleanup()

        # Memory after cleanup
        after_cleanup_memory = self.log_memory_usage('After Cleanup')

        return {
            'initial_memory': initial_memory,
            'after_cache_memory': after_cache_memory,
            'after_cleanup_memory': after_cleanup_memory,
            'cleanup_stats': cleanup_stats,
            'cache_increase': (
                after_cache_memory['current_mb'] - initial_memory['current_mb']
            ),
            'cleanup_reduction': (
                after_cache_memory['current_mb'] -
                after_cleanup_memory['current_mb']
            ),
        }

    async def test_handler_operations(self, call_py) -> Dict[str, Any]:
        """Test handler operations and memory usage"""
        logger.info('Testing handler operations...')

        initial_memory = self.log_memory_usage('Handler Test Start')

        # Add multiple handlers
        for i in range(100):
            def handler_factory(idx: int):
                def handler_func(update):
                    return f"Handler {idx} processed: {update}"
                return handler_func

            call_py.add_handler(handler_factory(i))

        after_handlers_memory = self.log_memory_usage('After Adding Handlers')

        # Clear handlers
        call_py._callbacks.clear()

        after_clear_memory = self.log_memory_usage('After Clearing Handlers')

        return {
            'initial_memory': initial_memory,
            'after_handlers_memory': after_handlers_memory,
            'after_clear_memory': after_clear_memory,
            'handler_increase': (
                after_handlers_memory['current_mb'] -
                initial_memory['current_mb']
            ),
            'clear_reduction': (
                after_handlers_memory['current_mb'] -
                after_clear_memory['current_mb']
            ),
        }

    async def test_chat_lock_operations(self, call_py) -> Dict[str, Any]:
        """Test chat lock operations and memory usage"""
        logger.info('Testing chat lock operations...')

        initial_memory = self.log_memory_usage('Chat Lock Test Start')

        # Create multiple chat locks
        tasks = []
        for i in range(50):
            task = asyncio.create_task(
                call_py._chat_lock.acquire(i),
            )
            tasks.append(task)

        # Wait for all locks to be acquired
        locks = await asyncio.gather(*tasks)

        after_locks_memory = self.log_memory_usage('After Creating Locks')

        # Release all locks
        for lock in locks:
            await lock.__aexit__(None, None, None)

        # Clear all locks
        await call_py._chat_lock.clear_all()

        after_clear_memory = self.log_memory_usage('After Clearing Locks')

        return {
            'initial_memory': initial_memory,
            'after_locks_memory': after_locks_memory,
            'after_clear_memory': after_clear_memory,
            'lock_increase': (
                after_locks_memory['current_mb'] - initial_memory['current_mb']
            ),
            'clear_reduction': (
                after_locks_memory['current_mb'] -
                after_clear_memory['current_mb']
            ),
        }

    async def test_comprehensive_cleanup(self, call_py) -> Dict[str, Any]:
        """Test comprehensive cleanup operations"""
        logger.info('Testing comprehensive cleanup...')

        initial_memory = self.log_memory_usage('Comprehensive Test Start')

        # Perform various operations
        for i in range(500):
            # Cache operations
            call_py._cache_user_peer.put(i, {'data': f'value_{i}' * 50})

            # Add handlers
            def handler_factory(idx: int):
                def handler_func(update):
                    return f"Handler {idx}"
                return handler_func
            call_py.add_handler(handler_factory(i))

            # Add to internal caches
            call_py._p2p_configs[i] = {'config': f'p2p_{i}'}
            call_py._call_sources[i] = {'source': f'source_{i}'}
            call_py._presentations.add(i)

            if i % 50 == 0:
                await asyncio.sleep(0.01)

        after_operations_memory = self.log_memory_usage('After Operations')

        # Comprehensive cleanup
        await call_py.shutdown()

        after_shutdown_memory = self.log_memory_usage('After Shutdown')

        return {
            'initial_memory': initial_memory,
            'after_operations_memory': after_operations_memory,
            'after_shutdown_memory': after_shutdown_memory,
            'operations_increase': (
                after_operations_memory['current_mb'] -
                initial_memory['current_mb']
            ),
            'shutdown_reduction': (
                after_operations_memory['current_mb'] -
                after_shutdown_memory['current_mb']
            ),
        }

    def print_test_summary(self):
        """Print summary of all test results"""
        logger.info('=' * 60)
        logger.info('MEMORY MANAGEMENT TEST SUMMARY')
        logger.info('=' * 60)

        for test_name, results in self.test_results.items():
            logger.info(f"\n{test_name.upper()}:")
            logger.info('-' * 40)

            if 'cache_increase' in results:
                logger.info(
                    f"Cache Increase: {results['cache_increase']:.2f}MB",
                )
                logger.info(
                    f"Cleanup Reduction: {results['cleanup_reduction']:.2f}MB",
                )

            if 'handler_increase' in results:
                logger.info(
                    f"Handler Increase: {results['handler_increase']:.2f}MB",
                )
                logger.info(
                    f"Clear Reduction: {results['clear_reduction']:.2f}MB",
                )

            if 'lock_increase' in results:
                logger.info(f"Lock Increase: {results['lock_increase']:.2f}MB")
                logger.info(
                    f"Clear Reduction: {results['clear_reduction']:.2f}MB",
                )

            if 'operations_increase' in results:
                logger.info(
                    (
                        f"Operations Increase: "
                        f"{results['operations_increase']:.2f}MB"
                    ),
                )
                logger.info(
                    (
                        f"Shutdown Reduction: "
                        f"{results['shutdown_reduction']:.2f}MB"
                    ),
                )

        # Final memory stats
        final_memory = self.get_memory_usage()
        logger.info('\nFINAL MEMORY USAGE:')
        logger.info(
            f"Current: {final_memory['current_mb']:.2f}MB",
        )
        logger.info(
            f"Peak: {final_memory['peak_mb']:.2f}MB",
        )


async def main():
    """Main test function"""
    logger.info('Starting Memory Management Tests...')

    # Start memory tracking
    tracemalloc.start()

    # Create test instance
    test = MemoryTest()

    try:
        # Note: In a real test, you would initialize PyTgCalls here
        # For demonstration, we'll create a mock object with the
        # required attributes

        class MockPyTgCalls:
            def __init__(self):
                from pytgcalls.types import Cache
                from pytgcalls.chat_lock import ChatLock
                self._cache_user_peer = Cache()
                self._chat_lock = ChatLock()
                self._callbacks = []
                self._p2p_configs = {}
                self._call_sources = {}
                self._presentations = set()

            def add_handler(self, func):
                self._callbacks.append(func)

            async def force_cleanup(self):
                return {'user_peer_cache': {'cleaned': 0}}

            async def shutdown(self):
                self._cache_user_peer.clear()
                self._callbacks.clear()
                self._p2p_configs.clear()
                self._call_sources.clear()
                self._presentations.clear()
                await self._chat_lock.clear_all()

        # Create mock PyTgCalls instance
        call_py = MockPyTgCalls()

        # Run tests
        test.test_results['cache_test'] = await test.test_cache_operations(
            call_py,
        )
        test.test_results['handler_test'] = await test.test_handler_operations(
            call_py,
        )
        test.test_results[
            'chat_lock_test'
        ] = await test.test_chat_lock_operations(
            call_py,
        )

        # Create new instance for comprehensive test
        call_py2 = MockPyTgCalls()
        comprehensive_result = await test.test_comprehensive_cleanup(
            call_py2,
        )
        test.test_results['comprehensive_test'] = (
            comprehensive_result
        )

        # Print summary
        test.print_test_summary()

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise
    finally:
        # Stop memory tracking
        tracemalloc.stop()


if __name__ == '__main__':
    asyncio.run(main())
