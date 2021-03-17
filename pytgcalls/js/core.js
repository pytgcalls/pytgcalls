const io = require('socket.io-client');
const RTCConnection = require('./rtc_connection');
const ApiSender = require('./api_sender');

(async () => {
    const port = process.argv[2].split('=')[1];
    const log_mode = parseInt(process.argv[3].split('=')[1]);
    let socket = io('ws://localhost:' + port);
    console.log('Starting on port: ' + port);
    socket.on('connect', async function () {
        console.log('\x1b[32m', 'Started NodeJS Core!', '\x1b[0m');
    });

    const apiSender = new ApiSender();
    let list_connection = [];

    await socket.on('request', async function (data) {
        data = JSON.parse(data);

        if (log_mode > 0) {
            console.log('REQUEST: ', data);
        }

        if (data['action'] === 'join_call') {
            if (!list_connection[data['chat_id']]) {
                list_connection[data['chat_id']] = new RTCConnection(
                    data['chat_id'],
                    data['file_path'],
                    port,
                    data['bitrate'],
                    log_mode,
                    data['buffer_long'],
                );

                let result = await list_connection[data['chat_id']].join_voice_call();
                if (result) {
                    await apiSender.sendUpdate(port, {
                        result: 'JOINED_VOICE_CHAT',
                        chat_id: data['chat_id'],
                    });
                } else {
                    delete list_connection[data['chat_id']];
                    await apiSender.sendUpdate(port, {
                        result: 'JOIN_ERROR',
                        chat_id: data['chat_id'],
                    });
                }
                if (log_mode > 0) {
                    console.log('UPDATED_LIST_OF_CONNECTIONS: ', list_connection);
                }
            }
        } else if (data['action'] === 'leave_call') {
            if (list_connection[data['chat_id']]) {
                if (data['type'] !== 'kicked_from_group') {
                    let result = await list_connection[data['chat_id']].leave_group_call(data['chat_id']);
                    if (result['result'] === 'OK') {
                        delete list_connection[data['chat_id']];
                        await apiSender.sendUpdate(port, {
                            result: 'LEAVED_VOICE_CHAT',
                            chat_id: data['chat_id'],
                        });
                    } else {
                        if (log_mode > 0) {
                            console.log('ERROR_INTERNAL: ', result);
                        }
                        delete list_connection[data['chat_id']];
                        await apiSender.sendUpdate(port, {
                            result: 'LEAVED_VOICE_CHAT',
                            error: result['result'],
                            chat_id: data['chat_id'],
                        });
                    }
                } else {
                    delete list_connection[data['chat_id']];
                    await apiSender.sendUpdate(port, {
                        result: 'KICKED_FROM_GROUP',
                        chat_id: data['chat_id'],
                    });
                }
            }
        } else if (data['action'] === 'pause') {
            if (list_connection[data['chat_id']]) {
                try {
                    await list_connection[data['chat_id']].pause();
                    await apiSender.sendUpdate(port, {
                        result: 'PAUSED_AUDIO_STREAM',
                        chat_id: data['chat_id'],
                    });
                } catch (e) {}
            }
        } else if (data['action'] === 'resume') {
            if (list_connection[data['chat_id']]) {
                try {
                    await list_connection[data['chat_id']].resume();
                    await apiSender.sendUpdate(port, {
                        result: 'RESUMED_AUDIO_STREAM',
                        chat_id: data['chat_id'],
                    });
                } catch (e) {}
            }
        } else if (data['action'] === 'change_stream') {
            if (list_connection[data['chat_id']]) {
                try {
                    await list_connection[data['chat_id']].change_stream(data['chat_id'], data['file_path']);
                    await apiSender.sendUpdate(port, {
                        result: 'CHANGED_AUDIO_STREAM',
                        chat_id: data['chat_id'],
                    });
                } catch (e) {}
            }
        }
    });
})();
