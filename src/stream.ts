import { EventEmitter } from 'events';
import {RTCAudioSource, nonstandard, RTCVideoSource} from 'wrtc';
import { Binding } from './binding';
import {RemotePlayingTimeCallback} from "./types";

export class Stream extends EventEmitter {
    private readonly audioSource: RTCAudioSource;
    private readonly videoSource: RTCVideoSource;
    private cache: Buffer;
    public paused: boolean = false;
    public finished: boolean = true;
    public stopped: boolean = false;
    private finishedLoading = false;
    private bytesLoaded: number = 0;
    private playedBytes: number = 0;
    private bytesSpeed: number = 0;
    private lastLag: number = 0;
    private equalCount: number = 0;
    private lastBytesLoaded: number = 0;
    private finishedBytes: boolean = false;
    private lastByteCheck: number = 0;
    private lastByte: number = 0;
    private runningPulse: boolean = false;
    private isVideo: boolean = false;
    private videoWidth: number = 0;
    private videoHeight: number = 0;
    private videoFramerate: number = 0;
    private lastDifferenceRemote: number = 0;
    remotePlayingTime?: RemotePlayingTimeCallback;

    constructor(
        public readable?: any,
        readonly bitsPerSample: number = 16,
        public sampleRate: number = 48000,
        readonly channelCount: number = 1,
        readonly buffer_length: number = 10,
        readonly timePulseBuffer: number = buffer_length == 4 ? 1.5 : 0,
    ) {
        super();
        this.audioSource = new nonstandard.RTCAudioSource();
        this.videoSource = new nonstandard.RTCVideoSource();
        this.cache = Buffer.alloc(0);
        this.paused = true;
        if(this.readable !== undefined){
            this.setReadable(this.readable);
        }
        setTimeout(
            () => this.processData(),
            1,
        );
    }

    setReadable(readable?: any) {
        if (this.readable !== readable) {
            this.readable.stop();
        }
        this.bytesLoaded = 0;
        this.bytesSpeed = 0;
        this.lastLag = 0;
        this.equalCount = 0;
        this.lastBytesLoaded = 0;
        this.finishedBytes = false;
        this.lastByteCheck = 0;
        this.lastByte = 0;
        this.playedBytes = 0;
        this.readable = readable;
        this.cache = Buffer.alloc(0);
        this.readable.resume();

        if (this.stopped) {
            throw new Error('Cannot set readable when stopped');
        }

        if (this.readable != undefined) {
            this.finished = false;
            this.finishedLoading = false;

            this.readable.onData = this.dataListener;
            this.readable.onEnd = this.endListener;
        }
    }

    private endListener = (async () => {
        this.finishedLoading = true;
        if(this.readable !== undefined){
            Binding.log(
                'COMPLETED_BUFFERING -> ' + new Date().getTime() +
                            ' -> ' + (this.isVideo ? 'VIDEO':'AUDIO'),
                Binding.DEBUG,
            );
            Binding.log(
                'BYTES_STREAM_CACHE_LENGTH -> ' + this.cache.length +
                            ' -> ' + (this.isVideo ? 'VIDEO':'AUDIO'),
                Binding.DEBUG,
            );
            Binding.log(
                'BYTES_LOADED -> ' +
                    this.bytesLoaded +
                    'OF -> ' +
                    await this.readable.fileSize() +
                            ' -> ' + (this.isVideo ? 'VIDEO':'AUDIO'),
                Binding.DEBUG,
            );
        }
    }).bind(this);

    private dataListener = (async (data: any) => {
        this.bytesLoaded += data.length;
        this.bytesSpeed = data.length;
        try {
            if (!(await this.needsBuffering())) {
                this.readable?.pause();
                this.runningPulse = false;
            }
        } catch (e) {
            this.emit('stream_deleted');
            return;
        }
        this.cache = Buffer.concat([this.cache, data]);
    }).bind(this);

    private needed_time(){
        return this.isVideo ? 0.30:50;
    }

    private async needsBuffering(withPulseCheck = true) {
        if (this.finishedLoading || this.readable === undefined) {
            return false;
        }

        let result = this.cache.length < this.bytesLength() * this.needed_time() * this.buffer_length;
        result =
            result &&
            (this.bytesLoaded <
                await this.readable.fileSize() -
                    this.bytesSpeed * 2 ||
                this.finishedBytes);

        if (this.timePulseBuffer > 0 && withPulseCheck) {
            result = result && this.runningPulse;
        }

        return result;
    }

    private checkLag() {
        if (this.finishedLoading) {
            return false;
        }

        return this.cache.length < this.bytesLength() * this.needed_time();
    }

    pause() {
        if (this.stopped) {
            throw new Error('Cannot pause when stopped');
        }

        this.paused = true;
        this.emit('pause', this.paused);
    }

    resume() {
        if (this.stopped) {
            throw new Error('Cannot resume when stopped');
        }

        this.paused = false;
        this.emit('resume', this.paused);
    }

    finish() {
        this.readable.stop();
        this.finished = true;
    }

    stop() {
        this.finish();
        this.stopped = true;
    }

    createAudioTrack() {
        return this.audioSource.createTrack();
    }

    createVideoTrack(width: number, height: number, framerate: number) {
        this.videoWidth = width;
        this.videoHeight = height;
        this.isVideo = true;
        this.videoFramerate = 1000 / framerate;
        return this.videoSource.createTrack();
    }

    setVideoParams(width: number, height: number, framerate: number) {
        this.videoWidth = width;
        this.videoHeight = height;
        this.videoFramerate = 1000 / framerate;
    }

    setAudioParams(bitrate: number) {
        this.sampleRate = bitrate;
    }

    private bytesLength(): number{
        if(this.isVideo) {
            return 1.5 * this.videoWidth * this.videoHeight;
        }else{
            return ((this.sampleRate * this.bitsPerSample) / 8 / 100) * this.channelCount;
        }
    }

    private async processData() {
        const oldTime = new Date().getTime();
        if (this.stopped) {
            return;
        }
        const byteLength = this.bytesLength();
        this.lastDifferenceRemote = 0;

        if (
            !(
                !this.finished &&
                this.finishedLoading &&
                this.cache.length < byteLength
            ) && this.readable !== undefined
        ) {
            try {
                if ((await this.needsBuffering(false))) {
                    let checkBuff = true;
                    if (this.timePulseBuffer > 0) {
                        this.runningPulse =
                            this.cache.length <
                            byteLength * this.needed_time() * this.timePulseBuffer;
                        checkBuff = this.runningPulse;
                    }
                    if (this.readable !== undefined && checkBuff) {
                        this.readable.resume();
                    }
                }
            } catch (e) {
                this.emit('stream_deleted');
                return;
            }

            const checkLag = this.checkLag();
            let fileSize: number;
            try {
                if (oldTime - this.lastByteCheck > 1000) {
                    fileSize = await this.readable.fileSize();
                    this.lastByte = fileSize;
                    this.lastByteCheck = oldTime;
                } else {
                    fileSize = this.lastByte;
                }
            } catch (e) {
                this.emit('stream_deleted');
                return;
            }
            const lagging_remote = this.isLaggingRemote();
            if (
                !this.paused &&
                !this.finished &&
                !lagging_remote &&
                (this.cache.length >= byteLength || this.finishedLoading) &&
                !checkLag
            ) {
                this.playedBytes += byteLength;
                const buffer = this.cache.slice(0, byteLength);
                if(this.isVideo) {
                    const i420Frame = {
                        width: this.videoWidth,
                        height: this.videoHeight,
                        data: new Uint8ClampedArray(buffer)
                    };
                    this.videoSource.onFrame(i420Frame)
                }else{
                    const samples = new Int16Array(new Uint8Array(buffer).buffer);
                    this.audioSource.onData({
                        bitsPerSample: this.bitsPerSample,
                        sampleRate: this.sampleRate,
                        channelCount: this.channelCount,
                        numberOfFrames: samples.length,
                        samples,
                    });
                }
                this.cache = this.cache.slice(byteLength);
            } else if (checkLag) {
                Binding.log(
                    'STREAM_LAG -> ' + new Date().getTime() +
                        ' -> ' + (this.isVideo ? 'VIDEO':'AUDIO'),
                    Binding.DEBUG,
                );
                Binding.log(
                    'BYTES_STREAM_CACHE_LENGTH -> ' + this.cache.length +
                        ' -> ' + (this.isVideo ? 'VIDEO':'AUDIO'),
                    Binding.DEBUG,
                );
                Binding.log(
                    'BYTES_LOADED -> ' +
                        this.bytesLoaded +
                        'OF -> ' +
                        await this.readable.fileSize() +
                        ' -> ' + (this.isVideo ? 'VIDEO':'AUDIO'),
                    Binding.DEBUG,
                );
            }

            if (!this.finishedLoading) {
                if (fileSize === this.lastBytesLoaded) {
                    if (this.equalCount >= 4) {
                        this.equalCount = 0;
                        Binding.log(
                            'NOT_ENOUGH_BYTES -> ' + oldTime +
                        ' -> ' + (this.isVideo ? 'VIDEO':'AUDIO'),
                            Binding.DEBUG,
                        );
                        this.finishedBytes = true;
                        this.readable?.resume();
                    } else {
                        if (oldTime - this.lastLag > 1000) {
                            this.equalCount += 1;
                            this.lastLag = oldTime;
                        }
                    }
                } else {
                    this.lastBytesLoaded = fileSize;
                    this.equalCount = 0;
                    this.finishedBytes = false;
                }
            }
        }

        if (
            !this.finished &&
            this.finishedLoading &&
            this.cache.length < byteLength &&
            this.readable !== undefined
        ) {
            this.finish();
            this.emit('finish');
        }

        const toSubtract = new Date().getTime() - oldTime;
        const timeoutWait = this.frameTime() - toSubtract - this.lastDifferenceRemote;
        setTimeout(
            async () => await this.processData(),
            timeoutWait > 0 ? timeoutWait:1,
        );
    }

    private isLaggingRemote(){
        if(this.remotePlayingTime != undefined) {
            const remote_play_time = this.remotePlayingTime().time;
            const local_play_time = this.currentPlayedTime();
            if (remote_play_time != undefined && local_play_time != undefined) {
                if(local_play_time > remote_play_time){
                    this.lastDifferenceRemote = (local_play_time - remote_play_time) * 100000;
                    return true;
                }
            }
        }
        return false;
    }

    private frameTime(): number{
        return (
            this.finished || this.paused || this.checkLag() || this.readable === undefined ? 500 : this.isVideo ? this.videoFramerate:10
        );
    }

    currentPlayedTime(): number | undefined{
        if(this.readable === undefined || this.playedBytes <= this.bytesLength() || this.finished){
            return undefined;
        }else{
            return Math.floor((this.playedBytes/this.bytesLength()) / (0.00001 / this.frameTime()))
        }
    }
}
