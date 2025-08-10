import asyncio
import logging
import os
import weakref
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from ntgcalls import NTgCalls

from .chat_lock import ChatLock
from .environment import Environment
from .methods import Methods
from .mtproto import MtProtoClient
from .scaffold import Scaffold
from .statictypes import statictypes
from .types import Cache

py_logger = logging.getLogger('pytgcalls')


class PyTgCalls(Methods, Scaffold):
    WORKERS = min(32, (os.cpu_count() or 0) + 4)
    CACHE_DURATION = 60 * 60

    @statictypes
    def __init__(
        self,
        app: Any,
        workers: int = WORKERS,
        cache_duration: int = CACHE_DURATION,
        enable_memory_manager: bool = True,
        memory_cleanup_interval: int = 300,
    ):
        super().__init__()
        self._mtproto = app
        self._app = MtProtoClient(
            cache_duration,
            self._mtproto,
        )
        self._is_running = False
        self._env_checker = Environment(
            self._REQUIRED_PYROGRAM_VERSION,
            self._REQUIRED_TELETHON_VERSION,
            self._REQUIRED_HYDROGRAM_VERSION,
            self._app.package_name,
        )
        self._cache_user_peer = Cache()
        self._binding = NTgCalls()
        self.loop = asyncio.get_event_loop()
        self.workers = workers
        self._chat_lock = ChatLock()
        self.executor = ThreadPoolExecutor(
            self.workers,
            thread_name_prefix='Handler',
        )
        # Add weak reference for cleanup
        self._finalizer = weakref.finalize(self, self._cleanup_resources)

        # Initialize memory manager
        self._memory_manager = None
        if enable_memory_manager:
            try:
                from .memory_manager import MemoryManager
                self._memory_manager = MemoryManager(
                    self,
                    cleanup_interval=memory_cleanup_interval,
                )
            except ImportError:
                # psutil might not be installed
                pass

    async def shutdown(self):
        """Properly shutdown PyTgCalls and cleanup all resources"""
        if self._is_running:
            self._is_running = False

            # Stop memory manager
            if self._memory_manager:
                self._memory_manager.stop()

            # Shutdown executor
            if hasattr(self, 'executor') and self.executor:
                self.executor.shutdown(wait=True)
                self.executor = None

            # Clear all caches
            if hasattr(self, '_cache_user_peer'):
                self._cache_user_peer.clear()

            # Clear all internal caches
            self._clear_all_caches()

            # Clear handlers
            if hasattr(self, '_callbacks'):
                self._callbacks.clear()

            # Clear chat locks
            if hasattr(self, '_chat_lock'):
                await self._chat_lock.clear_all()

            # Stop binding
            if hasattr(self, '_binding') and self._binding:
                try:
                    # Clear all active calls
                    calls = await self.calls
                    for chat_id in calls:
                        try:
                            await self._binding.stop(chat_id)
                        except (ConnectionError, RuntimeError, Exception) as e:
                            # Log specific errors but don't fail shutdown
                            py_logger.debug(
                                f"Error stopping call {chat_id}: {e}",
                            )
                            pass
                except (AttributeError, RuntimeError, Exception) as e:
                    # Log binding cleanup errors but don't fail shutdown
                    py_logger.debug(f"Error during binding cleanup: {e}")
                    pass
                self._binding = None

    def _clear_all_caches(self):
        """Clear all internal caches to prevent memory leaks"""
        if hasattr(self, '_p2p_configs'):
            self._p2p_configs.clear()
        if hasattr(self, '_call_sources'):
            self._call_sources.clear()
        if hasattr(self, '_wait_connect'):
            self._wait_connect.clear()
        if hasattr(self, '_presentations'):
            self._presentations.clear()
        if hasattr(self, '_pending_connections'):
            self._pending_connections.clear()
        if hasattr(self, '_need_unmute'):
            self._need_unmute.clear()

    def _cleanup_resources(self):
        """Cleanup resources when object is garbage collected"""
        if hasattr(self, 'executor') and self.executor:
            self.executor.shutdown(wait=False)

    async def start(self):
        """Start PyTgCalls with memory management"""
        await super().start()

        # Start memory manager if available
        if self._memory_manager:
            await self._memory_manager.start()

    async def force_cleanup(self) -> dict:
        """Force immediate memory cleanup and return statistics"""
        if self._memory_manager:
            return await self._memory_manager.force_cleanup()
        return {}

    def get_memory_stats(self) -> dict:
        """Get current memory statistics"""
        if self._memory_manager:
            return {
                'usage': self._memory_manager.get_memory_usage(),
                'increase': self._memory_manager.get_memory_increase(),
            }
        return {}

    @property
    def cache_user_peer(self) -> Cache:
        return self._cache_user_peer

    @property
    def mtproto_client(self):
        return self._mtproto
