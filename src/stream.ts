import { createReadStream, ReadStream, statSync } from 'fs';
import { EventEmitter } from 'events';
import {RTCAudioSource, nonstandard, RTCVideoSource} from 'wrtc';
import { Binding } from './binding';

export class Stream extends EventEmitter {
    private readonly audioSource: RTCAudioSource;
    private readonly videoSource: RTCVideoSource;
    private cache: Buffer;
    private readable?: ReadStream;
    public paused: boolean = false;
    public paused_sync_lag: boolean = false;
    public last_lag_status: boolean = false;
    public finished: boolean = true;
    public stopped: boolean = false;
    private finishedLoading = false;
    private bytesLoaded: number = 0;
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

    constructor(
        public filePath?: string,
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
        if(this.filePath !== undefined){
            this.setReadable(this.filePath);
        }
        this.processData();
    }

    setReadable(filePath?: string) {
        this.bytesLoaded = 0;
        this.bytesSpeed = 0;
        this.lastLag = 0;
        this.equalCount = 0;
        this.lastBytesLoaded = 0;
        this.finishedBytes = false;
        this.lastByteCheck = 0;
        this.lastByte = 0;
        this.paused_sync_lag = false;
        this.last_lag_status = false;

        if (this.readable) {
            this.readable.removeListener('data', this.dataListener);
            this.readable.removeListener('end', this.endListener);
        }
        this.filePath = filePath;
        if(filePath === undefined){
            this.readable = undefined;
            return;
        }
        this.readable = createReadStream(filePath);

        if (this.stopped) {
            throw new Error('Cannot set readable when stopped');
        }

        this.cache = Buffer.alloc(0);

        if (this.readable !== undefined) {
            this.finished = false;
            this.finishedLoading = false;

            this.readable.on('data', this.dataListener);
            this.readable.on('end', this.endListener);
        }
    }

    private endListener = (() => {
        this.finishedLoading = true;
        if(this.filePath !== undefined){
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
                    Stream.getFilesizeInBytes(this.filePath) +
                            ' -> ' + (this.isVideo ? 'VIDEO':'AUDIO'),
                Binding.DEBUG,
            );
        }
    }).bind(this);

    private dataListener = ((data: any) => {
        this.bytesLoaded += data.length;
        this.bytesSpeed = data.length;
        try {
            if (!this.needsBuffering()) {
                this.readable?.pause();
                this.runningPulse = false;
            }
        } catch (e) {
            this.emit('stream_deleted');
            return;
        }
        this.cache = Buffer.concat([this.cache, data]);
    }).bind(this);

    private static getFilesizeInBytes(path: string) {
        return statSync(path).size;
    }

    private needsBuffering(withPulseCheck = true) {
        if (this.finishedLoading || this.filePath === undefined) {
            return false;
        }

        const byteLength =
            ((this.sampleRate * this.bitsPerSample) / 8 / 100) *
            this.channelCount;
        let result = this.cache.length < byteLength * 100 * this.buffer_length;
        result =
            result &&
            (this.bytesLoaded <
                Stream.getFilesizeInBytes(this.filePath) -
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

        const byteLength =
            ((this.sampleRate * this.bitsPerSample) / 8 / 100) *
            this.channelCount;
        return this.cache.length < byteLength * 100;
    }

    pause() {
        if (this.stopped) {
            throw new Error('Cannot pause when stopped');
        }

        this.paused = true;
        this.emit('pause', this.paused);
    }

    set_sync_lag(status: boolean) {
        this.paused_sync_lag = status;
    }

    resume() {
        if (this.stopped) {
            throw new Error('Cannot resume when stopped');
        }

        this.paused = false;
        this.emit('resume', this.paused);
    }

    finish() {
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

    private processData() {
        const oldTime = new Date().getTime();
        if (this.stopped) {
            return;
        }
        let byteLength;
        if(this.isVideo) {
            byteLength = 1.5 * this.videoWidth * this.videoHeight;
        }else{
            byteLength = ((this.sampleRate * this.bitsPerSample) / 8 / 100) * this.channelCount;
        }

        if (
            !(
                !this.finished &&
                this.finishedLoading &&
                this.cache.length < byteLength
            ) && this.filePath !== undefined
        ) {
            try {
                if (this.needsBuffering(false)) {
                    let checkBuff = true;
                    if (this.timePulseBuffer > 0) {
                        this.runningPulse =
                            this.cache.length <
                            byteLength * 100 * this.timePulseBuffer;
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
            if(checkLag !== this.last_lag_status){
                this.last_lag_status = checkLag;
                this.emit('sync_lag', checkLag);
            }
            let fileSize: number;
            try {
                if (oldTime - this.lastByteCheck > 1000) {
                    fileSize = Stream.getFilesizeInBytes(this.filePath);
                    this.lastByte = fileSize;
                    this.lastByteCheck = oldTime;
                } else {
                    fileSize = this.lastByte;
                }
            } catch (e) {
                this.emit('stream_deleted');
                return;
            }

            if (
                !this.paused &&
                !this.paused_sync_lag &&
                !this.finished &&
                (this.cache.length >= byteLength || this.finishedLoading) &&
                !checkLag
            ) {
                if(this.isVideo) {
                    const buffer = this.cache.slice(0, byteLength);
                    this.cache = this.cache.slice(byteLength);
                    const i420Frame = {
                        width: this.videoWidth,
                        height: this.videoHeight,
                        data: new Uint8ClampedArray(buffer)
                    };
                    this.videoSource.onFrame(i420Frame)
                }else{
                    const buffer = this.cache.slice(0, byteLength);
                    const samples = new Int16Array(new Uint8Array(buffer).buffer);
                    this.cache = this.cache.slice(byteLength);
                    try {
                        this.audioSource.onData({
                            bitsPerSample: this.bitsPerSample,
                            sampleRate: this.sampleRate,
                            channelCount: this.channelCount,
                            numberOfFrames: samples.length,
                            samples,
                        });
                    } catch (error) {
                        this.emit('error', error);
                    }
                }

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
                        Stream.getFilesizeInBytes(this.filePath) +
                        ' -> ' + (this.isVideo ? 'VIDEO':'AUDIO'),
                    Binding.DEBUG,
                );
            }

            if (!this.finishedLoading) {
                if (fileSize === this.lastBytesLoaded) {
                    if (this.equalCount >= 8) {
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
            this.filePath !== undefined
        ) {
            this.finish();
            this.emit('finish');
        }

        const toSubtract = new Date().getTime() - oldTime;
        setTimeout(
            () => this.processData(),
            (
                this.finished || this.paused || this.checkLag() || this.filePath === undefined ? 500 : this.isVideo ? this.videoFramerate:10
            ) - toSubtract,
        );
    }

    sleep(ms: number) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
