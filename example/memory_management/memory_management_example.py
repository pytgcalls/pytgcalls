import asyncio
import logging
import time

from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message

from pytgcalls import idle
from pytgcalls import PyTgCalls

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

# Initialize clients
app = Client(
    'memory_management_example',
    api_id=123456789,
    api_hash='your_api_hash_here',
)

# Initialize PyTgCalls with memory management enabled
call_py = PyTgCalls(
    app,
    enable_memory_manager=True,  # Enable memory management
    memory_cleanup_interval=60,  # Cleanup every 60 seconds
    cache_duration=300,  # Cache duration 5 minutes
)


@app.on_message(filters.command('memory'))
async def memory_command(client: Client, message: Message):
    """Get current memory statistics"""
    stats = call_py.get_memory_stats()

    if stats:
        usage = stats['usage']
        increase = stats['increase']

        response = (
            '📊 **Memory Statistics**\n\n'
            '**Current Usage:**\n'
            f"• RSS: {usage['rss_mb']:.1f} MB\n"
            f"• VMS: {usage['vms_mb']:.1f} MB\n"
            f"• Percent: {usage['percent']:.1f}%\n"
            f"• Available: {usage['available_mb']:.1f} MB\n\n"
            '**Memory Increase:**\n'
            f"• RSS: +{increase['rss_increase_mb']:.1f} MB\n"
            f"• VMS: +{increase['vms_increase_mb']:.1f} MB\n"
            f"• Percent: +{increase['percent_increase']:.1f}%"
        )
    else:
        response = '❌ Memory monitoring not available (psutil not installed)'

    await message.reply_text(response)


@app.on_message(filters.command('cleanup'))
async def cleanup_command(client: Client, message: Message):
    """Force immediate memory cleanup"""
    await message.reply_text('🧹 Performing memory cleanup...')

    start_time = time.time()
    stats = await call_py.force_cleanup()
    end_time = time.time()

    if stats:
        response = (
            f"✅ **Cleanup Completed** ({end_time - start_time:.2f}s)\n\n"
            '**Results:**\n'
        )

        if 'user_peer_cache' in stats:
            cache_stats = stats['user_peer_cache']
            response += (
                f"• User Peer Cache: {cache_stats['cleaned']} items cleaned\n"
                f"• Cache size: {cache_stats['before_size']} → "
                f"{cache_stats['after_size']}\n"
            )

        if 'client_cache' in stats:
            cache_stats = stats['client_cache']
            response += (
                f"• Client Cache: {cache_stats['cleaned']} items cleaned\n"
            )

        if 'garbage_collection' in stats:
            gc_stats = stats['garbage_collection']
            response += (
                f"• Garbage Collection: "
                f"{gc_stats['collected_objects']} objects collected\n"
            )
    else:
        response = '❌ Memory monitoring not available'

    await message.reply_text(response)


@app.on_message(filters.command('stress_test'))
async def stress_test_command(client: Client, message: Message):
    """Test memory usage with multiple operations"""
    await message.reply_text('🧪 Starting memory stress test...')

    # Simulate multiple operations that might cause memory leaks
    for i in range(100):
        # Create some temporary data
        temp_data = {
            f'key_{i}': f'value_{i}' * 1000,
            'timestamp': time.time(),
            'index': i,
        }

        # Simulate cache operations
        call_py._cache_user_peer.put(i, temp_data)

        if i % 10 == 0:
            await asyncio.sleep(0.1)  # Small delay

    # Force cleanup
    stats = await call_py.force_cleanup()

    response = (
        '✅ **Stress Test Completed**\n\n'
        '• Created 100 temporary cache entries\n'
        '• Performed cleanup\n'
    )

    if stats and 'user_peer_cache' in stats:
        cache_stats = stats['user_peer_cache']
        response += f"• Cleaned: {cache_stats['cleaned']} expired entries\n"

    await message.reply_text(response)


@app.on_message(filters.command('shutdown'))
async def shutdown_command(client: Client, message: Message):
    """Properly shutdown PyTgCalls"""
    await message.reply_text('🛑 Shutting down PyTgCalls...')

    # Proper shutdown with cleanup
    await call_py.shutdown()

    await message.reply_text('✅ PyTgCalls shutdown completed with cleanup')

# Start the application


async def main():
    await call_py.start()
    await idle()

if __name__ == '__main__':
    app.run(main())
