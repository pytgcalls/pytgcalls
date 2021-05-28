import { createReadStream, statSync } from 'fs';
import { EventEmitter } from 'events';
import { RTCAudioSource, nonstandard } from 'wrtc';

export class Stream extends EventEmitter {
    private readonly audioSource: RTCAudioSource;
    private cache: Buffer;
    private readable = undefined;
    public paused: boolean = false;
    public finished: boolean = true;
    public stopped: boolean = false;
    private finishedLoading = false;
    public file_path: string;
    private bytesLoaded: number = 0;
    private bytesSpeed: number = 0;
    private lastLag: number = 0;
    private equalCount: number = 0;
    private lastBytesLoaded: number = 0;
    private finishedBytes: boolean = false;
    private lastByteCheck: number = 0;
    private lastByte: number = 0;
    private runningPulse: boolean = false;

    constructor(
        file_path: string,
        readonly bitsPerSample: number = 16,
        readonly sampleRate: number = 48000,
        readonly channelCount: number = 1,
        readonly logMode: number = 0,
        readonly buffer_lenght: number = 10,
        readonly timePulseBuffer: number = buffer_lenght == 4 ? 1.5 : 0
    ) {
        super();

        this.audioSource = new nonstandard.RTCAudioSource();
        this.cache = Buffer.alloc(0);
        this.file_path = file_path;
        this.setReadable(file_path);
        this.processData();
    }

    setReadable(file_path: string) {
        this.bytesLoaded = 0;
        this.bytesSpeed = 0;
        this.lastLag = 0;
        this.equalCount = 0;
        this.lastBytesLoaded = 0;
        this.finishedBytes = false;
        this.lastByteCheck = 0;
        this.lastByte = 0;
        this.file_path = file_path;
        // @ts-ignore
        this.readable = createReadStream(file_path);

        if (this.stopped) {
            throw new Error('Cannot set readable when stopped');
        }

        this.cache = Buffer.alloc(0);

        if (this.readable !== undefined) {
            this.finished = false;
            this.finishedLoading = false;

            // @ts-ignore
            this.readable.on('data', (data: any) => {
                this.bytesLoaded += data.length;
                this.bytesSpeed = data.length;
                console.log('BYTES_SPEED ->', this.bytesSpeed)
                if (!this.needsBuffering()) {
                    // @ts-ignore
                    this.readable.pause();
                    this.runningPulse = false;
                    if (this.logMode > 1) {
                        console.log('ENDED_BUFFERING ->', new Date().getTime());
                        console.log(
                            'BYTES_STREAM_CACHE_LENGTH ->',
                            this.cache.length
                        );
                        if (this.logMode > 1) {
                            console.log('PULSE ->', this.runningPulse);
                        }
                    }
                }

                if (this.logMode > 1) {
                    // @ts-ignore
                    console.log(
                        'BYTES_LOADED ->',
                        this.bytesLoaded,
                        'OF ->',
                        Stream.getFilesizeInBytes(this.file_path)
                    );
                }

                this.cache = Buffer.concat([this.cache, data]);
            });
            // @ts-ignore
            this.readable.on('end', () => {
                this.finishedLoading = true;
                if (this.logMode > 1) {
                    console.log('COMPLETED_BUFFERING ->', new Date().getTime());
                    console.log(
                        'BYTES_STREAM_CACHE_LENGTH ->',
                        this.cache.length
                    );
                    console.log(
                        'BYTES_LOADED ->',
                        this.bytesLoaded,
                        'OF ->',
                        Stream.getFilesizeInBytes(this.file_path)
                    );
                }
            });
        }
    }

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
        let result = this.cache.length < byteLength * 100 * this.buffer_lenght;
        result =
            result &&
            (this.bytesLoaded <
                Stream.getFilesizeInBytes(this.file_path) -
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

    createTrack() {
        return this.audioSource.createTrack();
    }

    getIdSource() {
        return this.audioSource;
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
            if (this.needsBuffering(false)) {
                let checkBuff = true;
                if (this.timePulseBuffer > 0) {
                    this.runningPulse =
                        this.cache.length <
                        byteLength * 100 * this.timePulseBuffer;
                    checkBuff = this.runningPulse;
                }
                if (this.readable !== undefined && checkBuff) {
                    if (this.logMode > 1) {
                        console.log('PULSE ->', this.runningPulse);
                    }
                    // @ts-ignore
                    this.readable.resume();
                    if (this.logMode > 1) {
                        console.log('BUFFERING -> ', new Date().getTime());
                    }
                }
            }

            const checkLag = this.checkLag();
            let fileSize: number;

            if (oldTime - this.lastByteCheck > 1000) {
                fileSize = Stream.getFilesizeInBytes(this.file_path);
                this.lastByte = fileSize;
                this.lastByteCheck = oldTime;
            } else {
                fileSize = this.lastByte;
            }

            if (
                !this.paused &&
                !this.finished &&
                (this.cache.length >= byteLength || this.finishedLoading) &&
                !checkLag
            ) {
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
            } else if (checkLag) {
                if (this.logMode > 1) {
                    console.log('STREAM_LAG -> ', new Date().getTime());
                    console.log(
                        'BYTES_STREAM_CACHE_LENGTH ->',
                        this.cache.length
                    );
                    console.log(
                        'BYTES_LOADED ->',
                        this.bytesLoaded,
                        'OF ->',
                        fileSize
                    );
                }
            }

            if (!this.finishedLoading) {
                if (fileSize === this.lastBytesLoaded) {
                    if (this.equalCount >= 15) {
                        this.equalCount = 0;
                        if (this.logMode > 1) {
                            console.log('NOT_ENOUGH_BYTES ->', oldTime);
                        }
                        this.finishedBytes = true;
                        // @ts-ignore
                        this.readable.resume();
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
                toSubtract
        );
    }

    sleep(ms: number) {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }
}
