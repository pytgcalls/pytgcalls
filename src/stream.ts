import { EventEmitter } from 'events';
import {RTCAudioSource, nonstandard, RTCVideoSource} from 'wrtc';
import { Binding } from './binding';
import {RemoteLaggingCallback, RemotePlayingTimeCallback} from "./types";
import {FFmpegReader} from "./ffmpeg_reader";
import {FileReader} from "./file_reader";
import {BufferOptimized} from "./buffer_optimized";
import * as os from "os";

export class Stream extends EventEmitter {
    private readonly audioSource: RTCAudioSource;
    private readonly videoSource: RTCVideoSource;
    private cache: BufferOptimized;
    public paused: boolean = false;
    public finished: boolean = true;
    public stopped: boolean = false;
    public stopped_done: boolean = false;
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
    private lipSync: boolean = false;
    private bytesLength: number = 0;
    private overloadQuiet: boolean = false;
    remotePlayingTime?: RemotePlayingTimeCallback;
    remoteLagging?: RemoteLaggingCallback;

    constructor(
        public readable?: FFmpegReader | FileReader,
        readonly bitsPerSample: number = 16,
        public sampleRate: number = 48000,
        readonly channelCount: number = 1,
        readonly buffer_length: number = 10,
        readonly timePulseBuffer: number = buffer_length == 4 ? 1.5 : 0,
    ) {
        super();
        this.audioSource = new nonstandard.RTCAudioSource();
        this.videoSource = new nonstandard.RTCVideoSource();
        this.paused = true;
        this.cache = new BufferOptimized(this.bytesLength);
        if(this.readable !== undefined){
            this.setReadable(this.readable);
        }
        setTimeout(
            () => this.processData(),
            1,
        );
    }

    public setLipSyncStatus(status: boolean){
        this.lipSync = status;
    }

    public setOverloadQuietStatus(status: boolean){
        this.overloadQuiet = status;
    }

    setReadable(readable?: FFmpegReader | FileReader) {
        this.finished = true;
        this.finishedLoading = false;
        this.bytesLoaded = 0;
        this.playedBytes = 0;
        this.bytesSpeed = 0;
        this.lastLag = 0;
        this.equalCount = 0;
        this.lastBytesLoaded = 0;
        this.finishedBytes = false;
        this.lastByteCheck = 0;
        this.lastByte = 0;
        this.runningPulse = false;
        this.lastDifferenceRemote = 0;
        this.readable = readable;
        this.bytesLength = this.bytesLengthCalculated();
        this.cache = new BufferOptimized(this.bytesLength);
        this.readable?.resume();

        if (this.stopped) {
            return;
        }

        if (this.readable != undefined) {
            this.finished = false;
            this.finishedLoading = false;
            this.readable.onData = this.dataListener;
            this.readable.onEnd = this.endListener;
        }
    }

    private endListener = (() => {
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
                this.readable.fileSize() +
                ' -> ' + (this.isVideo ? 'VIDEO':'AUDIO'),
                Binding.DEBUG,
            );
        }
    });

    private dataListener = ((data: any) => {
        this.bytesLoaded += data.length;
        this.bytesSpeed = data.length;
        try {
            if (!(this.needsBuffering())) {
                this.readable?.pause();
                this.runningPulse = false;
            }
        } catch (e) {
            this.emit('stream_deleted');
            return;
        }
        this.cache.push(data);
    }).bind(this);

    private needed_time(){
        return this.isVideo ? 0.30:50;
    }

    private needsBuffering(withPulseCheck = true) {
        if (this.finishedLoading || this.readable === undefined) {
            return false;
        }

        let result = this.cache.length < this.bytesLength * this.needed_time() * this.buffer_length;
        result =
            result &&
            (this.bytesLoaded <
                this.readable.fileSize() -
                this.bytesSpeed * 2 ||
                this.finishedBytes
            );

        if (this.timePulseBuffer > 0 && withPulseCheck) {
            result = result && this.runningPulse;
        }

        return result;
    }

    public checkLag() {
        if (this.finishedLoading) {
            return false;
        }
        return this.cache.length < this.bytesLength * this.needed_time();
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
        this.readable?.stop();
        this.finished = true;
        this.finishedLoading = true;
    }

    stop() {
        this.finish();
        this.stopped = true;
    }
    restart(readable?: FFmpegReader | FileReader) {
        this.stopped = true;
        setTimeout(() => {
            if(this.stopped_done){
                this.stopped = false;
                this.stopped_done = false;
                this.emit('restarted', readable);
                this.processData();
            }else{
                this.restart(readable);
            }
        }, 10);
    }

    createAudioTrack() {
        return this.audioSource.createTrack();
    }

    createVideoTrack(width: number, height: number, framerate: number) {
        this.videoWidth = width;
        this.videoHeight = height;
        this.isVideo = true;
        this.videoFramerate = 1000 / framerate;
        this.bytesLength = this.bytesLengthCalculated();
        this.cache.byteLength = this.bytesLength;
        return this.videoSource.createTrack();
    }

    setVideoParams(width: number, height: number, framerate: number) {
        this.videoWidth = width;
        this.videoHeight = height;
        this.videoFramerate = 1000 / framerate;
        this.bytesLength = this.bytesLengthCalculated();
        this.cache.byteLength = this.bytesLength;
    }

    setAudioParams(bitrate: number) {
        this.sampleRate = bitrate;
        this.bytesLength = this.bytesLengthCalculated();
        this.cache.byteLength = this.bytesLength;
    }

    private bytesLengthCalculated(): number{
        if(this.isVideo) {
            return 1.5 * this.videoWidth * this.videoHeight;
        }else{
            return ((this.sampleRate * this.bitsPerSample) / 8 / 100) * this.channelCount;
        }
    }

    private processData() {
        const oldTime = new Date().getTime();
        if (this.stopped) {
            this.stopped_done = true;
            return;
        }
        const lagging_remote = this.isLaggingRemote();
        const byteLength = this.bytesLength;
        const timeoutWait = this.frameTime()  - this.lastDifferenceRemote;
        setTimeout(
            () => this.processData(),
            timeoutWait > 0 ? timeoutWait:0,
        );
        if (
            !(
                !this.finished &&
                this.finishedLoading &&
                this.cache.length < byteLength
            ) && this.readable !== undefined
        ) {
            try {
                if ((this.needsBuffering(false))) {
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
                this.stopped = true;
                return;
            }

            const checkLag = this.checkLag();
            let fileSize: number;
            try {
                if (oldTime - this.lastByteCheck > 1000) {
                    fileSize = this.readable.fileSize();
                    this.lastByte = fileSize;
                    this.lastByteCheck = oldTime;
                } else {
                    fileSize = this.lastByte;
                }
            } catch (e) {
                this.emit('stream_deleted');
                this.stopped = true;
                return;
            }
            if (
                !this.paused &&
                !this.finished &&
                !lagging_remote &&
                (this.cache.length >= byteLength || this.finishedLoading) &&
                !checkLag
            ) {
                this.playedBytes += byteLength;
                const buffer = this.cache.readBytes();
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
            } else if (checkLag) {
                this.notifyOverloadCpu((cpuPercentage: number) => {
                    if(cpuPercentage >= 90){
                        Binding.log(
                            'CPU_OVERLOAD_DETECTED -> ' + new Date().getTime() +
                            ' -> ' + (this.isVideo ? 'VIDEO':'AUDIO'),
                            !this.overloadQuiet ? Binding.WARNING:Binding.DEBUG,
                        );
                    }else{
                        Binding.log(
                            'STREAM_LAG -> ' + new Date().getTime() +
                            ' -> ' + (this.isVideo ? 'VIDEO':'AUDIO'),
                            Binding.DEBUG,
                        );
                    }
                    Binding.log(
                        'BYTES_STREAM_CACHE_LENGTH -> ' + this.cache.length +
                        ' -> ' + (this.isVideo ? 'VIDEO':'AUDIO'),
                        Binding.DEBUG,
                    );
                    Binding.log(
                        'BYTES_LOADED -> ' +
                        this.bytesLoaded +
                        'OF -> ' +
                        this.readable?.fileSize() +
                        ' -> ' + (this.isVideo ? 'VIDEO':'AUDIO'),
                        Binding.DEBUG,
                    );
                });
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
    }

    public haveEnd(){
        if(this.readable != undefined){
            return this.readable.haveEnd;
        }else{
            return true;
        }
    }

    private isLaggingRemote(){
        if(this.remotePlayingTime != undefined && !this.paused && this.lipSync && this.remoteLagging != undefined) {
            const remote_play_time = this.remotePlayingTime().time;
            const local_play_time = this.currentPlayedTime();
            if (remote_play_time != undefined && local_play_time != undefined) {
                if(local_play_time > remote_play_time){
                    this.lastDifferenceRemote = (local_play_time - remote_play_time) * 10000;
                    return true;
                }else if(this.remoteLagging().isLagging && remote_play_time > local_play_time){
                    this.lastDifferenceRemote = 0;
                    return true;
                }
            }
        }
        return false;
    }
    private notifyOverloadCpu(action: (cpuPercentage: number) => void){
        function cpuAverage() {
            let totalIdle = 0, totalTick = 0;
            const cpus = os.cpus();
            for(let i = 0, len = cpus.length; i < len; i++) {
                const cpu = cpus[i];
                for(let type in cpu.times) {
                    totalTick += (<any> cpu).times[type];
                }
                totalIdle += cpu.times.idle;
            }
            return {idle: totalIdle / cpus.length,  total: totalTick / cpus.length};
        }
        const startMeasure = cpuAverage();
        setTimeout(function() {
            const endMeasure = cpuAverage();
            const idleDifference = endMeasure.idle - startMeasure.idle;
            const totalDifference = endMeasure.total - startMeasure.total;
            const percentageCPU = 100 - ~~(100 * idleDifference / totalDifference);
            action(percentageCPU);
        }, 500);
    }

    private frameTime(): number{
        return (
            this.finished || this.paused || this.checkLag() || this.readable === undefined ? 500 : this.isVideo ? this.videoFramerate:10
        );
    }

    currentPlayedTime(): number | undefined{
        if(this.readable === undefined || this.finished){
            return undefined;
        }else{
            return Math.ceil((this.playedBytes/this.bytesLength) / (0.0001 / this.frameTime()))
        }
    }
}
