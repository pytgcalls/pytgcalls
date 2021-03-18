const { TGCalls, Stream } = require('./lib');
const fetch = require('node-fetch');


class RTCConnection {
    #tgcalls = null;
    #stream = null;
    #sign_source = 0;
    #port_request = 0;
    #current_logging = 0;

    constructor(chat_id, path_file, port, bitrate, log_mode, buffer_long) {
        this.#port_request = port;
        this.#tgcalls = new TGCalls();
        this.#current_logging = log_mode;
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
            if (log_mode > 0) {
                console.log('request_join_call request -> ', request_join_call);
            }
            const req = await fetch('http://localhost:' + this.#port_request + '/request_join_call', {
                method: 'POST',
                body: JSON.stringify(request_join_call),
            });
            const result = await req.json();
            if (log_mode > 0) {
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
            if (log_mode > 0) {
                console.log('get_participants result -> ', result);
            }
            return result;
        };

        this.#stream = new Stream(path_file, 16, bitrate, 1, log_mode, buffer_long);

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
            this.#stream.stop();
            if (this.#current_logging > 1) {
                console.log('JOIN_VOICE_CALL_ERROR ->', e)
            }
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

    async resume() {
        this.#stream.resume();
    }

    change_stream(chat_id, path_file) {
        this.#stream.setReadable(path_file);
    }
}

module.exports = RTCConnection;
