// @ts-ignore
import {connect} from 'socket.io-client';
import {RTCConnection} from './rtc-connection';
import {Binding} from './binding'

(async () => {
    let py_bind = new Binding();
    py_bind.on('connect', async (user_id: number) =>
        console.log('\x1b[32m', '[' + user_id + '] Started Node.js Core!', '\x1b[0m')
    );
    let connections: Array<RTCConnection> = [];
    py_bind.on('request', async function (data: any) {
        Binding.log('REQUEST: ' + JSON.stringify(data), Binding.INFO);
        if (data.action === 'join_call') {
            if (!connections[data.chat_id]) {
                connections[data.chat_id] = new RTCConnection(
                    data.chat_id,
                    data.file_path,
                    py_bind,
                    data.bitrate,
                    data.buffer_length,
                    data.invite_hash,
                );

                const result = await connections[data.chat_id].joinCall();
                if (result) {
                    await py_bind.sendUpdate({
                        action: 'update_request',
                        result: 'JOINED_VOICE_CHAT',
                        chat_id: data.chat_id,
                    });
                } else {
                    delete connections[data.chat_id];
                    await py_bind.sendUpdate({
                        result: 'JOIN_ERROR',
                        chat_id: data.chat_id,
                    });
                }
            }
        } else if (data.action === 'leave_call') {
            if (connections[data.chat_id]) {
                if (data.type !== 'kicked_from_group') {
                    let result = await connections[data.chat_id].leave_call();

                    if (result['result'] === 'OK') {
                        delete connections[data.chat_id];
                        await py_bind.sendUpdate({
                            action: 'update_request',
                            result: 'LEFT_VOICE_CHAT',
                            chat_id: data.chat_id,
                        });
                    } else {
                        delete connections[data.chat_id];
                        await py_bind.sendUpdate({
                            action: 'update_request',
                            result: 'LEFT_VOICE_CHAT',
                            error: result['result'],
                            chat_id: data.chat_id,
                        });
                    }
                } else {
                    await connections[data.chat_id].stop();
                    delete connections[data.chat_id];
                }
            }
        } else if (data.action === 'pause') {
            if (connections[data.chat_id]) {
                try {
                    await connections[data.chat_id].pause();
                    await py_bind.sendUpdate({
                        action: 'update_request',
                        result: 'PAUSED_AUDIO_STREAM',
                        chat_id: data.chat_id,
                    });
                } catch (e) {}
            }
        } else if (data.action === 'resume') {
            if (connections[data.chat_id]) {
                try {
                    await connections[data.chat_id].resume();
                    await py_bind.sendUpdate({
                        action: 'update_request',
                        result: 'RESUMED_AUDIO_STREAM',
                        chat_id: data.chat_id,
                    });
                } catch (e) {}
            }
        } else if (data.action === 'change_stream') {
            if (connections[data.chat_id]) {
                try {
                    await connections[data.chat_id].changeStream(data.file_path);
                    await py_bind.sendUpdate({
                        action: 'update_request',
                        result: 'CHANGED_AUDIO_STREAM',
                        chat_id: data.chat_id,
                    });
                } catch (e) {}
            }
        }
    });
})();
