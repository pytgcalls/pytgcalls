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

    constructor(
        public filePath: string,
        readonly bitsPerSample: number = 16,
        readonly sampleRate: number = 48000,
        readonly channelCount: number = 1,
        readonly buffer_length: number = 10,
        readonly timePulseBuffer: number = buffer_length == 4 ? 1.5 : 0,
    ) {
        super();

        this.audioSource = new nonstandard.RTCAudioSource();
        this.videoSource = new nonstandard.RTCVideoSource();
        this.cache = Buffer.alloc(0);
        this.paused = true;
        this.setReadable(this.filePath);
        this.processData();
    }

    setReadable(filePath: string) {
        this.bytesLoaded = 0;
        this.bytesSpeed = 0;
        this.lastLag = 0;
        this.equalCount = 0;
        this.lastBytesLoaded = 0;
        this.finishedBytes = false;
        this.lastByteCheck = 0;
        this.lastByte = 0;

        if (this.readable) {
            this.readable.removeListener('data', this.dataListener);
            this.readable.removeListener('end', this.endListener);
        }

        this.filePath = filePath;
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
        Binding.log(
            'COMPLETED_BUFFERING -> ' + new Date().getTime(),
            Binding.DEBUG,
        );
        Binding.log(
            'BYTES_STREAM_CACHE_LENGTH -> ' + this.cache.length,
            Binding.DEBUG,
        );
        Binding.log(
            'BYTES_LOADED -> ' +
                this.bytesLoaded +
                'OF -> ' +
                Stream.getFilesizeInBytes(this.filePath),
            Binding.DEBUG,
        );
    }).bind(this);

    private dataListener = ((data: any) => {
        this.bytesLoaded += data.length;
        this.bytesSpeed = data.length;
        try {
            if (!this.needsBuffering()) {
                this.readable?.pause();
                this.runningPulse = false;
                Binding.log(
                    'ENDED_BUFFERING -> ' + new Date().getTime(),
                    Binding.DEBUG,
                );
                Binding.log(
                    'BYTES_STREAM_CACHE_LENGTH -> ' + this.cache.length,
                    Binding.DEBUG,
                );
                Binding.log('PULSE -> ' + this.runningPulse, Binding.DEBUG);
            }
        } catch (e) {
            this.emit('stream_deleted');
            return;
        }

        Binding.log(
            'BYTES_LOADED -> ' +
                this.bytesLoaded +
                'OF -> ' +
                Stream.getFilesizeInBytes(this.filePath),
            Binding.DEBUG,
        );
        this.cache = Buffer.concat([this.cache, data]);
    }).bind(this);

    private static getFilesizeInBytes(path: string) {
        return statSync(path).size;
    }

    private needsBuffering(withPulseCheck = true) {
        if (this.finishedLoading) {
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

    createVideoTrack(width: number, height: number) {
        this.videoWidth = width;
        this.videoHeight = height;
        this.isVideo = true;
        return this.videoSource.createTrack();
    }

    private processData() {
        const oldTime = new Date().getTime();
        if (this.stopped) {
            return;
        }

        const byteLength =
            ((this.sampleRate * this.bitsPerSample) / 8 / 100) *
            this.channelCount;

        if (
            !(
                !this.finished &&
                this.finishedLoading &&
                this.cache.length < byteLength
            )
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
                        Binding.log(
                            'PULSE -> ' + this.runningPulse,
                            Binding.DEBUG,
                        );
                        this.readable.resume();
                        Binding.log(
                            'BUFFERING -> ' + new Date().getTime(),
                            Binding.DEBUG,
                        );
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
                !this.finished &&
                (this.cache.length >= byteLength || this.finishedLoading) &&
                !checkLag
            ) {
                if(this.isVideo) {
                    const buffer = this.cache.slice(0, byteLength);
                    const samples = new Int16Array(new Uint8Array(buffer).buffer)
                    this.cache = this.cache.slice(byteLength);
                    // HERE IS WRONG VIDEO SENDING
                    const i420Frame = {
                        width: this.videoWidth,
                        height: this.videoHeight,
                        data: new Uint8ClampedArray(samples)
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
                    'STREAM_LAG -> ' + new Date().getTime(),
                    Binding.DEBUG,
                );
                Binding.log(
                    'BYTES_STREAM_CACHE_LENGTH -> ' + this.cache.length,
                    Binding.DEBUG,
                );
                Binding.log(
                    'BYTES_LOADED -> ' +
                        this.bytesLoaded +
                        'OF -> ' +
                        Stream.getFilesizeInBytes(this.filePath),
                    Binding.DEBUG,
                );
            }

            if (!this.finishedLoading) {
                if (fileSize === this.lastBytesLoaded) {
                    if (this.equalCount >= 15) {
                        this.equalCount = 0;
                        Binding.log(
                            'NOT_ENOUGH_BYTES -> ' + oldTime,
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
            this.cache.length < byteLength
        ) {
            this.finish();
            this.emit('finish');
        }

        const toSubtract = new Date().getTime() - oldTime;
        setTimeout(
            () => this.processData(),
            (this.finished || this.paused || this.checkLag() ? 500 : 10) -
                toSubtract,
        );
    }

    sleep(ms: number) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
