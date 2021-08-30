import { Stream, TGCalls } from './tgcalls';
import { Binding } from './binding';

export class RTCConnection {
    tgcalls: TGCalls<any>;
    audioStream: Stream;
    //videoStream: Stream;

    constructor(
        public chatId: number,
        public filePath: string,
        public binding: Binding,
        public bitrate: number,
        public bufferLength: number,
        public inviteHash: string,
    ) {
        this.tgcalls = new TGCalls({ chatId: this.chatId });
        this.audioStream = new Stream(filePath, 16, bitrate, 1, bufferLength);
        // this.videoStream = new Stream('test.iv4', 16, bitrate, 1, bufferLength);

        this.tgcalls.joinVoiceCall = async (payload: any) => {
            payload = {
                chat_id: this.chatId,
                ufrag: payload.ufrag,
                pwd: payload.pwd,
                hash: payload.hash,
                setup: payload.setup,
                fingerprint: payload.fingerprint,
                source: payload.source,
                invite_hash: this.inviteHash,
            };

            Binding.log(
                'callJoinPayload -> ' + JSON.stringify(payload),
                Binding.INFO,
            );

            const joinCallResult = await this.binding.sendUpdate({
                action: 'join_voice_call_request',
                payload: payload,
            });

            Binding.log(
                'joinCallRequestResult -> ' + JSON.stringify(joinCallResult),
                Binding.INFO,
            );

            return joinCallResult;
        };
        this.audioStream.on('finish', async () => {
            await this.binding.sendUpdate({
                action: 'stream_ended',
                chat_id: chatId,
            });
        });
        this.audioStream.on('stream_deleted', async () => {
            this.audioStream.stop();

            await this.binding.sendUpdate({
                action: 'update_request',
                result: 'STREAM_DELETED',
                chat_id: chatId,
            });
        });
    }

    async joinCall() {
        try {
            let result = await this.tgcalls.start(this.audioStream.createAudioTrack());
            this.audioStream.resume();
            //this.videoStream.resume();
            return result;
        } catch (e: any) {
            this.audioStream.stop();
            //this.videoStream.stop();
            Binding.log('joinCallError -> ' + e.toString(), Binding.INFO);
            return false;
        }
    }

    stop() {
        try {
            this.audioStream.stop();
            //this.videoStream.stop();
            this.tgcalls.close();
        } catch (e) {}
    }

    async leave_call() {
        try {
            this.stop();
            return await this.binding.sendUpdate({
                action: 'leave_call_request',
                chat_id: this.chatId,
            });
        } catch (e: any) {
            return {
                action: 'REQUEST_ERROR',
                message: e.toString(),
            };
        }
    }

    pause() {
        this.audioStream.pause();
        //this.videoStream.pause();
    }

    resume() {
        this.audioStream.resume();
        //this.videoStream.resume();
    }

    changeStream(filePath: string) {
        this.filePath = filePath;
        this.audioStream.setReadable(this.filePath);
    }
}
