const { TGCalls, Stream } = require('../../lib');
const fetch = require('node-fetch');
const fs = require('fs');

class RTCConnection {
    #tgcalls = null;
    #stream = null;
    #sign_source = 0;
    #port_request = 0;

    constructor(chat_id, path_file, port, bitrate, log_mode) {
        this.#port_request = port;
        this.#tgcalls = new TGCalls();

        this.#tgcalls.joinVoiceCall = async payload => {
            const request_join_call = {
                chat_id: chat_id,
                ufrag: payload.ufrag,
                pwd: payload.pwd,
                hash: payload.hash,
                setup: payload.setup,
                fingerprint: payload.fingerprint,
                source: payload.source,
            }
            if (log_mode) {
                console.log('request_join_call request -> ', request_join_call);
            }
            const req = await fetch('http://localhost:' + this.#port_request + '/request_join_call', {
                method: 'POST',
                body: JSON.stringify(request_join_call),
            });
            const result = await req.json();
            if (log_mode) {
                console.log('request_join_call result -> ', result);
            }
            return result;
        };

        this.#tgcalls.getParticipants = async () => {
            const req = await fetch('http://localhost:' + this.#port_request + '/get_participants', {
                method: 'POST',
                body: JSON.stringify({
                    chat_id: chat_id,
                }),
            });
            const result = await req.json();
            if (log_mode) {
                console.log('get_participants result -> ', result);
            }
            return result;
        };

        const readable = fs.createReadStream(path_file, { highWaterMark: 256 * 1024 });
        this.#stream = new Stream(readable, 16, bitrate, 1);

        this.#stream.OnStreamEnd = async () => {
            await fetch('http://localhost:' + this.#port_request + '/ended_stream', {
                method: 'POST',
                body: JSON.stringify({
                    chat_id: chat_id,
                }),
            });
        };
    }

    async join_voice_call() {
        try {
            const result = await this.#tgcalls.start(this.#stream.createTrack());
            this.#sign_source = this.#tgcalls.getSignSource();
            return result;
        } catch (e) {
            return false;
        }
    }

    async leave_group_call(chat_id) {
        try {
            this.#stream.stop();
            this.#tgcalls.close();
            return await (
                await fetch('http://localhost:' + this.#port_request + '/request_leave_call', {
                    method: 'POST',
                    body: JSON.stringify({
                        chat_id: chat_id,
                        sign_source: this.#sign_source,
                    }),
                })
            ).json();
        } catch (e) {
            return {
                action: 'REQUEST_ERROR',
                message: e.toString(),
            };
        }
    }

    pause() {
        this.#stream.pause();
    }

    resume() {
        this.#stream.resume();
    }

    change_stream(chat_id, path_file) {
        const readable = fs.createReadStream(path_file, { highWaterMark: 256 * 1024 });
        this.#stream.setReadable(readable);
    }
}

module.exports = RTCConnection;
