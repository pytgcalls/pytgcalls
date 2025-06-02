import asyncio
import json
import logging
import os
import signal
import time
from datetime import datetime

from telethon import TelegramClient
from telethon.sessions import StringSession

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls.events import ChatUpdate
from pytgcalls.events import StreamFrames
from pytgcalls.types import MediaStream
from pytgcalls.types import Update
from pytgcalls.types.calls import GroupCallParticipant
from pytgcalls.types.input_stream import InputAudioStream
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream import InputVideoStream
from pytgcalls.types.stream import Device
from pytgcalls.types.stream import Direction

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# --- Constants ---
API_ID = int(os.getenv('API_ID', '1234567'))  # Replace with your API_ID
API_HASH = os.getenv('API_HASH', 'abcdef1234567890abcdef1234567890')  # Replace
SESSION_STRING = os.getenv('SESSION_STRING')  # Optional, fill if you have one
# Replace with target chat ID
CHAT_ID = int(os.getenv('CHAT_ID', '-1001234567890'))

ROOT_ARCHIVE_DIR = 'TELEGRAM_CALL_ARCHIVES'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

# --- Global Variables ---
keep_running = True
pytg_app_global = None
telethon_client_global = None

call_metadata = {}
archive_dir_current_call = None

# Maps to manage SSRC, participants, and files
participant_info_map = {}  # SSRC -> participant details (name, id, etc.)
participant_to_ssrcs_map = {}  # participant_id -> set of SSRCs
ssrc_to_participant_id_map = {}  # SSRC -> participant_id
ssrc_to_file_map = {}  # SSRC -> file handle
# SSRC -> { 'media_type': 'audio'/'video', 'start_time_ms': ..., 'last_frame_timestamp_ms': ..., 'video_width': ..., 'video_height': ... }
ssrc_to_stream_metadata = {}


async def record_telegram_call(chat_id_to_record: int):
    global keep_running, pytg_app_global, telethon_client_global
    global call_metadata, archive_dir_current_call
    global participant_info_map, participant_to_ssrcs_map, ssrc_to_participant_id_map
    global ssrc_to_file_map, ssrc_to_stream_metadata

    logger.info(f"Initializing Telegram client...")
    if SESSION_STRING:
        telethon_client_global = TelegramClient(
            StringSession(SESSION_STRING), API_ID, API_HASH,
        )
    else:
        telethon_client_global = TelegramClient(
            'anon_recorder_session', API_ID, API_HASH,
        )

    await telethon_client_global.connect()
    if not await telethon_client_global.is_user_authorized():
        logger.error(
            'User is not authorized. Please run a script to log in and save session.',
        )
        # For interactive login:
        # await telethon_client_global.start()
        # print("Session string:", telethon_client_global.session.save())
        return

    logger.info('Telegram client initialized.')

    logger.info('Initializing PyTgCalls...')
    pytg_app_global = PyTgCalls(telethon_client_global)
    await pytg_app_global.start()
    logger.info('PyTgCalls initialized.')

    # Create archive directory
    call_start_time_str = datetime.now().strftime(DATETIME_FORMAT)
    archive_dir_current_call = os.path.join(
        ROOT_ARCHIVE_DIR, f"call_{chat_id_to_record}_{call_start_time_str}",
    )
    os.makedirs(archive_dir_current_call, exist_ok=True)
    logger.info(f"Archive directory created: {archive_dir_current_call}")

    call_metadata = {
        'chat_id': chat_id_to_record,
        'start_time_utc': datetime.utcnow().isoformat(),
        'streams': [],
    }

    # Register event handlers
    pytg_app_global.on_event(StreamFrames)(handle_stream_frames_event)
    # We might need ChatUpdate for more dynamic participant updates if periodic checks are not enough
    # pytg_app_global.on_event(ChatUpdate)(handle_chat_update_event) # Placeholder

    try:
        logger.info(
            f"Attempting to join call in chat {chat_id_to_record} as a listener.",
        )
        await pytg_app_global.play(
            chat_id_to_record,
            None,  # Join as listener
            listen_only_mode=True,
            # Consider specifying input_stream if None is not enough for listener mode
            # input_stream=InputStream(input_mode=InputAudioStream(path_to_file="silence.raw")) # Example for pure listening
        )
        logger.info(f"Successfully joined call in chat {chat_id_to_record}.")

        # Initial participant mapping
        await update_participant_and_ssrc_maps(chat_id_to_record)

        while keep_running:
            # Periodically update participant map as a fallback/main method
            await update_participant_and_ssrc_maps(chat_id_to_record)
            active_streams = len(ssrc_to_file_map)
            logger.debug(
                f"Recording in progress... {active_streams} active streams. Checking for stop signal.",
            )
            # Check every 5 seconds for participants and stop signal
            await asyncio.sleep(5)

    except Exception as e:
        logger.error(f"Error during call: {e}", exc_info=True)
    finally:
        logger.info('Initiating cleanup...')
        if pytg_app_global and pytg_app_global.is_running:
            try:
                logger.info(f"Leaving call in chat {chat_id_to_record}...")
                await pytg_app_global.leave_call(chat_id_to_record)
                logger.info('Left call.')
            except Exception as e:
                logger.error(f"Error leaving call: {e}", exc_info=True)

            try:
                logger.info('Stopping PyTgCalls client...')
                await pytg_app_global.stop()
                logger.info('PyTgCalls client stopped.')
            except Exception as e:
                logger.error(f"Error stopping PyTgCalls: {e}", exc_info=True)

        if telethon_client_global and telethon_client_global.is_connected():
            logger.info('Disconnecting Telethon client...')
            await telethon_client_global.disconnect()
            logger.info('Telethon client disconnected.')

        # Close all open media files
        for ssrc, file_handle in ssrc_to_file_map.items():
            try:
                file_handle.close()
                logger.info(f"Closed file for SSRC {ssrc}.")
            except Exception as e:
                logger.error(f"Error closing file for SSRC {ssrc}: {e}")
        ssrc_to_file_map.clear()

        # Finalize and save metadata
        call_metadata['end_time_utc'] = datetime.utcnow().isoformat()
        # Store copies of stream metadata
        call_metadata['streams'] = list(ssrc_to_stream_metadata.values())
        metadata_file_path = os.path.join(
            archive_dir_current_call, 'metadata.json',
        )
        try:
            with open(metadata_file_path, 'w') as f:
                json.dump(call_metadata, f, indent=4)
            logger.info(f"Call metadata saved to {metadata_file_path}")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")

        logger.info('Cleanup complete.')


async def update_participant_and_ssrc_maps(current_chat_id: int):
    global participant_info_map, participant_to_ssrcs_map, ssrc_to_participant_id_map

    if not pytg_app_global or not pytg_app_global.is_running:
        logger.warning(
            'PyTgCalls not running, cannot update participant maps.',
        )
        return

    try:
        call_info = (await pytg_app_global.calls).get(current_chat_id)
        if not call_info or not call_info.participants:
            logger.debug(
                f"No call info or participants found for chat {current_chat_id} to update maps.",
            )
            return

        current_participants = call_info.participants
        logger.debug(
            f"Found {len(current_participants)} participants in call {current_chat_id}.",
        )

        # Temporary maps for the current state
        new_participant_info_map = {}
        new_participant_to_ssrcs_map = {}
        new_ssrc_to_participant_id_map = {}

        for p_info in current_participants:  # p_info is GroupCallParticipant
            participant_id = p_info.user_id
            # Participant name requires a Telethon call, e.g., (await telethon_client_global.get_entity(participant_id)).first_name
            # For now, using a placeholder:
            participant_name = f"User_{participant_id}"

            if not participant_id:  # Should not happen if user_id is a direct attribute
                logger.warning(
                    f"Participant with no ID found (should be impossible): {p_info}. Skipping.",
                )
                continue

            new_participant_to_ssrcs_map.setdefault(participant_id, set())

            # Audio SSRC
            if p_info.source is not None:  # p_info.source is the audio SSRC
                ssrc_audio = p_info.source
                new_participant_info_map[ssrc_audio] = {
                    'id': participant_id, 'name': participant_name, 'type': 'audio',
                }
                new_participant_to_ssrcs_map[participant_id].add(ssrc_audio)
                new_ssrc_to_participant_id_map[ssrc_audio] = participant_id

            # Video SSRC
            if p_info.video_info and p_info.video_info.sources is not None and len(p_info.video_info.sources) > 0:
                for ssrc_group in p_info.video_info.sources:  # ssrc_group is SsrcGroup from ntgcalls
                    if hasattr(ssrc_group, 'ssrc'):
                        video_ssrc = ssrc_group.ssrc
                        new_participant_info_map[video_ssrc] = {
                            'id': participant_id, 'name': participant_name, 'type': 'video',
                        }
                        new_participant_to_ssrcs_map[participant_id].add(
                            video_ssrc,
                        )
                        new_ssrc_to_participant_id_map[video_ssrc] = participant_id
                        logger.info(
                            f"Found video SSRC {video_ssrc} for participant {participant_id} ({participant_name})",
                        )
                    else:
                        logger.warning(
                            f"Video SsrcGroup for participant {participant_id} ({participant_name}) does not have 'ssrc' attribute. SsrcGroup: {ssrc_group}",
                        )
            else:
                logger.debug(
                    f"No video sources or video_info for participant {participant_id} ({participant_name}). Video_info: {p_info.video_info}",
                )

            # Screen Share SSRC
            if p_info.presentation_info and p_info.presentation_info.sources is not None and len(p_info.presentation_info.sources) > 0:
                for ssrc_group in p_info.presentation_info.sources:  # ssrc_group is SsrcGroup from ntgcalls
                    if hasattr(ssrc_group, 'ssrc'):
                        screen_ssrc = ssrc_group.ssrc
                        new_participant_info_map[screen_ssrc] = {
                            'id': participant_id, 'name': participant_name, 'type': 'screen',
                        }
                        new_participant_to_ssrcs_map[participant_id].add(
                            screen_ssrc,
                        )
                        new_ssrc_to_participant_id_map[screen_ssrc] = participant_id
                        logger.info(
                            f"Found screen share SSRC {screen_ssrc} for participant {participant_id} ({participant_name})",
                        )
                    else:
                        logger.warning(
                            f"Screen share SsrcGroup for participant {participant_id} ({participant_name}) does not have 'ssrc' attribute. SsrcGroup: {ssrc_group}",
                        )
            else:
                logger.debug(
                    f"No presentation sources or presentation_info for participant {participant_id} ({participant_name}). Presentation_info: {p_info.presentation_info}",
                )

        # Update global maps (simple overwrite for now, could be more sophisticated)
        participant_info_map = new_participant_info_map
        participant_to_ssrcs_map = new_participant_to_ssrcs_map
        ssrc_to_participant_id_map = new_ssrc_to_participant_id_map

        logger.info(
            f"Participant maps updated. {len(participant_info_map)} SSRCs mapped.",
        )
        logger.debug(f"SSRC to PID map: {ssrc_to_participant_id_map}")
        logger.debug(f"PID to SSRCs map: {participant_to_ssrcs_map}")

    except Exception as e:
        logger.error(
            f"Error updating participant and SSRC maps: {e}", exc_info=True,
        )


async def handle_stream_frames_event(client: PyTgCalls, event: StreamFrames):
    global ssrc_to_file_map, ssrc_to_stream_metadata, archive_dir_current_call
    global participant_info_map, ssrc_to_participant_id_map

    if event.direction == Direction.OUTGOING:  # event is StreamFrames
        # logger.debug("Ignoring outgoing frames batch.")
        return

    for frame_obj in event.frames:  # frame_obj is Frame
        ssrc = frame_obj.ssrc
        participant_id = ssrc_to_participant_id_map.get(ssrc)
        participant_details = participant_info_map.get(ssrc)

        user_identifier = 'UnknownUser'
        if participant_details:
            # Name is already f"User_{participant_id}" or actual name if fetched
            user_identifier = f"{participant_details.get('name', f'User_{participant_id}')}"
        elif participant_id:
            user_identifier = f"User_{participant_id}"

        media_type = 'unknown'
        # Default for raw Opus audio (event.device == MICROPHONE)
        file_extension = 'raw'

        # Determine media type primarily from participant_info_map (set by SSRC type)
        # or fallback to event.device (which is for the whole batch of frames)
        if participant_details:
            media_type = participant_details.get('type', 'unknown')

        if media_type == 'audio' or (media_type == 'unknown' and (event.device == Device.MICROPHONE or event.device == Device.SPEAKER)):
            media_type = 'audio'
            file_extension = 'raw'  # Opus
        elif media_type == 'video' or (media_type == 'unknown' and event.device == Device.CAMERA):
            media_type = 'video'
            file_extension = 'h264'
        elif media_type == 'screen' or (media_type == 'unknown' and event.device == Device.SCREEN_SHARE):
            media_type = 'screen'
            file_extension = 'h264'

        # Update participant_details map if we just discovered a more specific type via event.device
        if participant_details and participant_details.get('type') == 'unknown' and media_type != 'unknown':
            participant_details['type'] = media_type
            logger.info(
                f"Updated media type for SSRC {ssrc} to {media_type} based on event.device",
            )

        if ssrc not in ssrc_to_file_map:
            if not archive_dir_current_call:
                logger.error(
                    f"Archive directory not set, cannot create file for SSRC {ssrc}",
                )
                continue  # Skip this frame_obj

            timestamp_now_ms = int(time.time() * 1000)
            # Ensure user_identifier is filesystem-safe, though current format should be okay.
            filename = f"{user_identifier}_SSRC_{ssrc}_{media_type}.{file_extension}"
            filepath = os.path.join(archive_dir_current_call, filename)

            try:
                ssrc_to_file_map[ssrc] = open(filepath, 'ab')  # Append binary
                logger.info(
                    f"Opened new file for SSRC {ssrc} ({media_type}): {filepath}",
                )

                video_width = frame_obj.info.width if frame_obj.info else None
                video_height = frame_obj.info.height if frame_obj.info else None

                ssrc_to_stream_metadata[ssrc] = {
                    'ssrc': ssrc,
                    'participant_id': participant_id if participant_id else 'Unknown',
                    'participant_name': participant_details.get('name', 'Unknown') if participant_details else 'Unknown',
                    'media_type': media_type,
                    'filename': filename,
                    'start_time_ms': frame_obj.info.capture_time if frame_obj.info and frame_obj.info.capture_time else timestamp_now_ms,
                    'last_frame_timestamp_ms': frame_obj.info.capture_time if frame_obj.info and frame_obj.info.capture_time else timestamp_now_ms,
                    'video_width': video_width,
                    'video_height': video_height,
                }
            except OSError as e:
                logger.error(
                    f"Error opening file for SSRC {ssrc}: {filepath}. Error: {e}",
                )
                if ssrc in ssrc_to_file_map:
                    del ssrc_to_file_map[ssrc]
                if ssrc in ssrc_to_stream_metadata:
                    del ssrc_to_stream_metadata[ssrc]
                continue  # Skip this frame_obj

        # Write frame data
        if ssrc in ssrc_to_file_map:
            try:
                frame_data = frame_obj.frame  # This is bytes

                if frame_data:
                    ssrc_to_file_map[ssrc].write(frame_data)

                    # Update metadata
                    current_capture_time_ms = frame_obj.info.capture_time if frame_obj.info and frame_obj.info.capture_time else int(
                        time.time() * 1000,
                    )
                    if ssrc in ssrc_to_stream_metadata:
                        ssrc_to_stream_metadata[ssrc]['last_frame_timestamp_ms'] = current_capture_time_ms
                        if frame_obj.info and frame_obj.info.width is not None:  # Check if info and width exist
                            ssrc_to_stream_metadata[ssrc]['video_width'] = frame_obj.info.width
                            ssrc_to_stream_metadata[ssrc]['video_height'] = frame_obj.info.height
                else:
                    logger.warning(
                        f"Received empty frame data for SSRC {ssrc}",
                    )

            except OSError as e:
                logger.error(f"Error writing to file for SSRC {ssrc}: {e}")
                # Consider closing file and removing from map if write fails persistently
            except Exception as e:
                logger.error(
                    f"Unexpected error processing frame for SSRC {ssrc}: {e}", exc_info=True,
                )


def signal_handler(sig, frame):
    global keep_running
    logger.info(f"Signal {sig} received, initiating graceful shutdown...")
    keep_running = False


async def main():
    # To ensure it's accessible in signal handler for cleanup if needed
    global pytg_app_global

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Basic input validation or interactive setup for CHAT_ID could be added here
    if not CHAT_ID:
        logger.error(
            'CHAT_ID is not set. Please set the environment variable or update the script.',
        )
        return

    # Ensure root archive directory exists
    os.makedirs(ROOT_ARCHIVE_DIR, exist_ok=True)

    await record_telegram_call(CHAT_ID)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt caught in main loop, shutting down...')
        # Ensure keep_running is set to False if loop was interrupted before signal handler
        keep_running = False
    finally:
        # This block might be redundant if record_telegram_call handles all cleanup,
        # but good for safety if main() itself has resources to clean.
        # Ensure all tasks are cancelled before closing loop, especially if main() creates tasks.
        tasks = [
            t for t in asyncio.all_tasks(
            ) if t is not asyncio.current_task()
        ]
        for task in tasks:
            task.cancel()
        if tasks:  # If there were tasks to cancel
            loop.run_until_complete(
                asyncio.gather(
                *tasks, return_exceptions=True,
                ),
            )

        # Final check for PyTgCalls cleanup if it wasn't done
        if pytg_app_global and pytg_app_global.is_running:
            logger.warning(
                'PyTgCalls still running in final cleanup, attempting to stop.',
            )
            loop.run_until_complete(pytg_app_global.stop())

        logger.info('Application finished.')
