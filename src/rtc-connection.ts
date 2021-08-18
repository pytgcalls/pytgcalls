// @ts-ignore
import fetch from 'node-fetch';
import {Stream, TGCalls} from './tgcalls';
import {Binding} from "./binding";

export class RTCConnection {
    chat_id: number;
    file_path: string;
    binding: Binding;
    bitrate: number;
    buffer_length: number;
    invite_hash: string;

    tgcalls: TGCalls<any>;
    stream: Stream;

    constructor(
        chat_id: number,
        file_path: string,
        binding: Binding,
        bitrate: number,
        buffer_length: number,
        invite_hash: string,
    ) {
        this.chat_id = chat_id;
        this.file_path = file_path;
        this.binding = binding;
        this.bitrate = bitrate;
        this.buffer_length = buffer_length;
        this.invite_hash = invite_hash;

        this.tgcalls = new TGCalls({chat_id});
        this.stream = new Stream(
            file_path,
            16,
            bitrate,
            1,
            buffer_length
        );

        this.tgcalls.joinVoiceCall = async (payload: any) => {
            payload = {
                chat_id: this.chat_id,
                ufrag: payload.ufrag,
                pwd: payload.pwd,
                hash: payload.hash,
                setup: payload.setup,
                fingerprint: payload.fingerprint,
                source: payload.source,
                invite_hash: this.invite_hash,
            };

            Binding.log('callJoinPayload -> ' + JSON.stringify(payload), Binding.INFO);

            const joinCallResult = await this.binding.sendUpdate({
                action: 'join_voice_call_request',
                payload: payload
            });

            Binding.log('joinCallRequestResult -> ' + JSON.stringify(joinCallResult), Binding.INFO);

            return joinCallResult;
        };

        this.stream.on('finish', async () => {
            await this.binding.sendUpdate({
                action: 'stream_ended',
                chat_id: chat_id,
            })
        });
    }

    async joinCall() {
        try {
            let result = await this.tgcalls.start(this.stream.createTrack());
            this.stream.resume()
            return result
        } catch (e) {
            this.stream.stop();
            Binding.log('joinCallError -> ' + e.toString(), Binding.INFO);
            return false;
        }
    }

    stop() {
        try {
            this.stream.stop();
            this.tgcalls.close();
        } catch (e) {}
    }

    async leave_call() {
        try {
            this.stop();
            return await this.binding.sendUpdate({
                action: 'leave_call_request',
                chat_id: this.chat_id,
            });
        } catch (e) {
            return {
                action: 'REQUEST_ERROR',
                message: e.toString(),
            };
        }
    }

    pause() {
        this.stream.pause();
    }

    async resume() {
        this.stream.resume();
    }

    changeStream(file_path: string) {
        this.stream.setReadable(file_path);
    }
}
