import { Stream, TGCalls } from './tgcalls';
import {Binding, MultiCoreBinding} from './binding';
import {FFmpegReader} from "./ffmpeg_reader";
import {FileReader} from "./file_reader";
import {LogLevel} from "./utils";

export class RTCConnection {
    tgcalls: TGCalls<any>;
    audioStream: Stream;
    videoStream: Stream;
    private almostFinished: number = 0;
    private almostRestarted: number = 0;
    private almostMaxFinished: number = 0;
    private waitingAudioReadable?: FFmpegReader | FileReader = undefined;
    private waitingVideoReadable?: FFmpegReader | FileReader = undefined;

    constructor(
        public chatId: number,
        public binding: MultiCoreBinding | Binding,
        public bufferLength: number,
        public inviteHash: string,
        public audioParams?: any,
        public videoParams?: any,
        lipSync: boolean = false,
        overloadQuiet: boolean = false,
    ) {
        this.tgcalls = new TGCalls({ chatId: this.chatId });
        const fileAudioPath = audioParams === undefined ? undefined:audioParams.path;
        const fileVideoPath = videoParams === undefined ? undefined:videoParams.path;
        let audioReadable;
        if(audioParams !== undefined){
            if(fileAudioPath.startsWith('fifo://') || fileAudioPath.startsWith('device://')){
                audioReadable = new FFmpegReader(audioParams.ffmpeg_parameters);
                audioReadable.convert_audio(
                    fileAudioPath,
                    audioParams.bitrate,
                );
            }else{
                audioReadable = new FileReader(
                    fileAudioPath,
                );
            }
        }
        let videoReadable;
        if(videoParams !== undefined){
            if(fileVideoPath.startsWith('fifo://') || fileVideoPath.startsWith('screen://')){
                videoReadable = new FFmpegReader(videoParams.ffmpeg_parameters);
                videoReadable.convert_video(
                    fileVideoPath,
                    videoParams.width,
                    videoParams.height,
                    videoParams.framerate,
                );
            }else{
                videoReadable = new FileReader(
                    fileVideoPath,
                );
            }
        }

        this.audioStream = new Stream(audioReadable, 16, audioParams ? audioParams.bitrate:0, 1, bufferLength);
        this.videoStream = new Stream(videoReadable);
        this.audioStream.setLipSyncStatus(lipSync);
        this.videoStream.setLipSyncStatus(lipSync);
        this.audioStream.setOverloadQuietStatus(overloadQuiet);
        this.videoStream.setOverloadQuietStatus(overloadQuiet);

        this.tgcalls.joinVoiceCall = async (payload: any) => {
            payload = {
                chat_id: this.chatId,
                ufrag: payload.ufrag,
                pwd: payload.pwd,
                hash: payload.hash,
                setup: payload.setup,
                fingerprint: payload.fingerprint,
                source: payload.source,
                source_groups: payload.source_groups,
                have_video: fileVideoPath === undefined,
                invite_hash: this.inviteHash,
            };

            Binding.log(
                'callJoinPayload -> ' + JSON.stringify(payload),
                LogLevel.INFO,
            );

            const joinCallResult = await this.binding.sendUpdate({
                action: 'join_voice_call_request',
                payload: payload,
            });

            Binding.log(
                'joinCallRequestResult -> ' + JSON.stringify(joinCallResult),
                LogLevel.INFO,
            );

            return joinCallResult;
        };
        this.almostFinished = 0;
        this.almostRestarted = 0;
        this.almostMaxFinished = 0;
        if(audioReadable != undefined){
            this.almostMaxFinished += 1;
        }
        if(videoReadable != undefined){
            this.almostMaxFinished += 1;
        }
        this.audioStream.on('finish', async () => {
            this.almostFinished += 1;
            if(!this.videoStream.haveEnd()){
                this.almostFinished += 1;
                this.videoStream.finish();
            }
            if(this.almostFinished === this.almostMaxFinished){
                this.almostFinished = 0;
                await this.binding.sendUpdate({
                    action: 'stream_audio_ended',
                    chat_id: chatId,
                });
                if(this.almostMaxFinished === 2){
                    await this.binding.sendUpdate({
                        action: 'stream_video_ended',
                        chat_id: chatId,
                    });
                }
            }
        });
        this.videoStream.on('finish', async () => {
            this.almostFinished += 1;
            if(this.almostFinished === this.almostMaxFinished){
                this.almostFinished = 0;
                await this.binding.sendUpdate({
                    action: 'stream_video_ended',
                    chat_id: chatId,
                });
                if(this.almostMaxFinished === 2){
                    await this.binding.sendUpdate({
                        action: 'stream_audio_ended',
                        chat_id: chatId,
                    });
                }
            }
        });
        this.audioStream.on('restarted', async (readable?: FFmpegReader | FileReader) => {
            this.almostRestarted += 1;
            this.waitingAudioReadable = readable;
            if(this.almostRestarted === 2){
                this.almostRestarted = 0;
                this.audioStream.setReadable(this.waitingAudioReadable);
                this.videoStream.setReadable(this.waitingVideoReadable);
            }
        });
        this.videoStream.on('restarted', async (readable?: FFmpegReader | FileReader) => {
            this.almostRestarted += 1;
            this.waitingVideoReadable = readable;
            if(this.almostRestarted === 2){
                this.almostRestarted = 0;
                this.audioStream.setReadable(this.waitingAudioReadable);
                this.videoStream.setReadable(this.waitingVideoReadable);
            }
        });
        this.audioStream.on('stream_deleted', async () => {
            this.audioStream.stop();
            this.videoStream.stop();
            await this.binding.sendUpdate({
                action: 'update_request',
                result: 'STREAM_DELETED',
                chat_id: chatId,
            });
        });
        this.videoStream.on('stream_deleted', async () => {
            this.audioStream.stop();
            this.videoStream.stop();
            await this.binding.sendUpdate({
                action: 'update_request',
                result: 'STREAM_DELETED',
                chat_id: chatId,
            });
        });
        this.audioStream.remotePlayingTime = () => {
            return {
                time: this.videoStream.currentPlayedTime()
            }
        };
        this.videoStream.remotePlayingTime = () => {
            return {
                time: this.audioStream.currentPlayedTime()
            }
        };
        this.audioStream.remoteLagging = () => {
            return {
                isLagging: this.videoStream.checkLag()
            }
        };
        this.videoStream.remoteLagging = () => {
            return {
                isLagging: this.audioStream.checkLag()
            }
        };
    }

    async joinCall(): Promise<void> {
        const setVideoParams = async () => ({
            width: this.videoParams === undefined ? 1:this.videoParams.width,
            height: this.videoParams === undefined ? 1:this.videoParams.height,
            framerate: this.videoParams === undefined ? 1:this.videoParams.framerate,
        });
        const createVideoTrack = ({width, height, framerate}: {width: number, height: number, framerate: number}) => this.videoStream.createVideoTrack(width, height, framerate);
        const startVoiceCall = async (videoTrack: MediaStreamTrack) =>  this.tgcalls.start(this.audioStream.createAudioTrack(), videoTrack).catch(err => {
            this.audioStream.stop();
            this.videoStream.stop();
            Binding.log('joinCallError -> ' + err.toString(), LogLevel.ERROR);
            throw err;
        }).then(() => {
            this.videoStream.resume();
            this.audioStream.resume();
        });
        return setVideoParams().then(createVideoTrack).then(startVoiceCall);
    }

    stop() {
        try {
            this.audioStream.stop();
            this.videoStream.stop();
            this.tgcalls.close();
        } catch (e) {}
    }

    async leave_call() {
        try {
            if(!this.tgcalls.isClosed()){
                this.stop();
                return await this.binding.sendUpdate({
                    action: 'leave_call_request',
                    chat_id: this.chatId,
                });
            }else{
                return null;
            }
        } catch (e: any) {
            return {
                action: 'REQUEST_ERROR',
                message: e.toString(),
            };
        }
    }

    async pause() {
        this.audioStream.pause();
        this.videoStream.pause();
        if(this.videoParams != undefined){
            await this.binding.sendUpdate({
                action: 'upgrade_video_status',
                chat_id: this.chatId,
                paused_status: true,
            });
        }
    }

    getTime() {
        let time = 0;
        if (this.audioStream != undefined) {
            time = this.audioStream.getCurrentPlayedTime();
        } else if (this.videoStream != undefined) {
            time = this.videoStream.getCurrentPlayedTime();
        }
        return Math.round(time / 10000000);
    }

    async resume() {
        this.audioStream.resume();
        this.videoStream.resume();
        if(this.videoParams != undefined){
            await this.binding.sendUpdate({
                action: 'upgrade_video_status',
                chat_id: this.chatId,
                paused_status: false,
            });
        }
    }

    mute() {
        this.tgcalls.mute();
    }

    unmute() {
        this.tgcalls.unmute();
    }

    async changeStream(audioParams?: any, videoParams?: any, lipSync: boolean = false) {
        let audioReadable;
        this.almostFinished = 0;
        this.almostRestarted = 0;
        this.almostMaxFinished = 0;
        if(audioParams != undefined){
            this.almostMaxFinished += 1;
        }
        if(videoParams != undefined){
            this.almostMaxFinished += 1;
        }
        if(audioParams != undefined){
            if(audioParams.path.startsWith('fifo://') || audioParams.path.startsWith('device://')){
                audioReadable = new FFmpegReader(audioParams.ffmpeg_parameters);
                audioReadable.convert_audio(
                    audioParams.path,
                    audioParams.bitrate,
                );
            }else{
                audioReadable = new FileReader(
                    audioParams.path,
                );
            }
        }
        let videoReadable;
        if(videoParams != undefined){
            if(videoParams.path.startsWith('fifo://') || videoParams.path.startsWith('screen://')){
                videoReadable = new FFmpegReader(videoParams.ffmpeg_parameters);
                videoReadable.convert_video(
                    videoParams.path,
                    videoParams.width,
                    videoParams.height,
                    videoParams.framerate,
                );
            }else{
                videoReadable = new FileReader(
                    videoParams.path,
                );
            }
        }
        this.audioParams = audioParams;
        if(this.audioParams != undefined){
            this.audioStream.setAudioParams(this.audioParams.bitrate);
        }
        if(
            !(this.videoParams == undefined && videoParams == undefined) ||
            !(this.videoParams != undefined && videoParams != undefined)
        ){
            await this.binding.sendUpdate({
                action: 'upgrade_video_status',
                chat_id: this.chatId,
                stopped_status: videoParams == undefined
            });
        }
        this.videoParams = videoParams;
        if(this.videoParams != undefined){
            this.videoStream.setVideoParams(
                this.videoParams.width,
                this.videoParams.height,
                this.videoParams.framerate,
            )
        }
        this.videoStream.readable?.stop();
        this.videoStream.readable = undefined;
        this.audioStream.readable?.stop();
        this.audioStream.readable = undefined;
        this.audioStream.setLipSyncStatus(lipSync);
        this.videoStream.setLipSyncStatus(lipSync);
        this.videoStream.restart(videoReadable);
        this.audioStream.restart(audioReadable);
    }
}
