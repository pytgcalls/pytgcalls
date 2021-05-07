// @ts-ignore
import { connect } from 'socket.io-client';
import RTCConnection from './rtc-connection';
import sendUpdate from './send-update';

(async () => {
    const port = parseInt(process.argv[2].split('=')[1]);
    const logMode = parseInt(process.argv[3].split('=')[1]);
    let socket = connect(`ws://localhost:${port}`);
    console.log('Starting on port: ' + port);
    socket.on('connect', () =>
        console.log('\x1b[32m', 'Started NodeJS Core!', '\x1b[0m')
    );

    let connections: Array<RTCConnection> = [];

    await socket.on('request', async function (data: any) {
        data = JSON.parse(data);

        if (logMode > 0) {
            console.log('REQUEST: ', data);
        }

        if (data['action'] === 'join_call') {
            if (!connections[data.chat_id]) {
                connections[data.chat_id] = new RTCConnection(
                    data.chat_id,
                    data['file_path'],
                    port,
                    data['bitrate'],
                    logMode,
                    data['buffer_lenght'],
                    data['invite_hash']
                );

                const result = await connections[data.chat_id].joinCall();

                if (result) {
                    await sendUpdate(port, {
                        result: 'JOINED_VOICE_CHAT',
                        chat_id: data.chat_id,
                    });
                } else {
                    delete connections[data.chat_id];
                    await sendUpdate(port, {
                        result: 'JOIN_ERROR',
                        chat_id: data.chat_id,
                    });
                }

                if (logMode > 0) {
                    console.log('UPDATED_CONNECTIONS: ', connections);
                }
            }
        } else if (data['action'] === 'leave_call') {
            if (connections[data.chat_id]) {
                if (data['type'] !== 'kicked_from_group') {
                    let result = await connections[data.chat_id].leave_call();

                    if (result['result'] === 'OK') {
                        delete connections[data.chat_id];
                        await sendUpdate(port, {
                            result: 'LEFT_VOICE_CHAT',
                            chat_id: data.chat_id,
                        });
                    } else {
                        if (logMode > 0) {
                            console.log('ERROR_INTERNAL: ', result);
                        }

                        delete connections[data.chat_id];
                        await sendUpdate(port, {
                            result: 'LEFT_VOICE_CHAT',
                            error: result['result'],
                            chat_id: data.chat_id,
                        });
                    }
                } else {
                    await connections[data.chat_id].stop();
                    delete connections[data.chat_id];
                    await sendUpdate(port, {
                        result: 'KICKED_FROM_GROUP',
                        chat_id: data.chat_id,
                    });
                }
            }
        } else if (data['action'] === 'pause') {
            if (connections[data.chat_id]) {
                try {
                    await connections[data.chat_id].pause();
                    await sendUpdate(port, {
                        result: 'PAUSED_AUDIO_STREAM',
                        chat_id: data.chat_id,
                    });
                } catch (e) {}
            }
        } else if (data['action'] === 'resume') {
            if (connections[data.chat_id]) {
                try {
                    await connections[data.chat_id].resume();
                    await sendUpdate(port, {
                        result: 'RESUMED_AUDIO_STREAM',
                        chat_id: data.chat_id,
                    });
                } catch (e) {}
            }
        } else if (data['action'] === 'change_stream') {
            if (connections[data.chat_id]) {
                try {
                    await connections[data.chat_id].changeStream(data.file_path);
                    await sendUpdate(port, {
                        result: 'CHANGED_AUDIO_STREAM',
                        chat_id: data.chat_id,
                    });
                } catch (e) {}
            }
        }
    });
})();
