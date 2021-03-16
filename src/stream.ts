import { EventEmitter } from 'events';
import { Readable } from 'stream';
import { RTCAudioSource, nonstandard } from 'wrtc';

export class Stream extends EventEmitter {
    private readonly audioSource: RTCAudioSource;
    private cache: Buffer;
    private local_readable = undefined;
    private _paused = false;
    private _finished = true;
    private _stopped = false;
    private OnStreamEnd = Function;
    private _finishedLoading = false;

    constructor(
        readable?: Readable,
        readonly bitsPerSample = 16,
        readonly sampleRate = 48000,
        readonly channelCount = 1,
        readonly log_mode = 0,
    ) {
        super();

        this.audioSource = new nonstandard.RTCAudioSource();
        this.cache = Buffer.alloc(0);
        this.setReadable(readable);
        this.processData();
    }

    setReadable(readable?: Readable) {
        // @ts-ignore
        this.local_readable = readable;
        if (this._stopped) {
            throw new Error('Cannot set readable when stopped');
        }

        this.cache = Buffer.alloc(0);

        if(this.local_readable !== undefined){
            this._finished = false;
            this._finishedLoading = false;

            // @ts-ignore
            this.local_readable.on('data', (data: any) => {

                if(!this.need_buffering()){
                    // @ts-ignore
                    this.local_readable.pause();
                    if(this.log_mode > 1){
                        console.log('ENDED_BUFFERING -> ', new Date().getTime());
                        console.log('BYTES_STREAM_CACHE_LENGTH -> ', this.cache.length);
                    }
                }
                this.cache = Buffer.concat([this.cache, data]);
            });
            // @ts-ignore
            this.local_readable.on('end', () => {
                this._finishedLoading = true;
                if(this.log_mode > 1){
                    console.log('ENDED_BUFFERING -> ', new Date().getTime());
                    console.log('BYTES_STREAM_CACHE_LENGTH -> ', this.cache.length);
                }
            });
        }
    }

    private need_buffering(){
        if(this._finishedLoading){
            return false;
        }
        const byteLength = ((this.sampleRate * this.bitsPerSample) / 8 / 100) * this.channelCount;
        return this.cache.length < (byteLength * 100) * 10;
    }

    private check_lag(){
        if(this._finishedLoading){
            return false;
        }
        const byteLength = ((this.sampleRate * this.bitsPerSample) / 8 / 100) * this.channelCount;
        return this.cache.length < (byteLength * 100) * 5;
    }
    pause() {
        if (this._stopped) {
            throw new Error('Cannot pause when stopped');
        }

        this._paused = true;
        this.emit('pause', this._paused);
    }

    resume() {
        if (this._stopped) {
            throw new Error('Cannot resume when stopped');
        }

        this._paused = false;
        this.emit('resume', this._paused);
    }

    get paused() {
        return this._paused;
    }

    finish() {
        this._finished = true;
    }

    get finished() {
        return this._finished;
    }

    stop() {
        this.finish();
        this._stopped = true;
    }

    get stopped() {
        return this._stopped;
    }

    createTrack() {
        return this.audioSource.createTrack();
    }

    getIdSource() {
        return this.audioSource;
    }

    private processData() {
        const old_time=new Date().getTime()
        if (this._stopped) {
            return;
        }

        const byteLength = ((this.sampleRate * this.bitsPerSample) / 8 / 100) * this.channelCount;

        if(this.need_buffering()){
            if(this.local_readable !== undefined){
                // @ts-ignore
                this.local_readable.resume();
                if(this.log_mode > 1){
                    console.log('BUFFERING -> ', new Date().getTime());
                }
            }
        }
        const check_lag = this.check_lag();
        if (!this._paused && !this._finished && (this.cache.length >= byteLength || this._finishedLoading) && !check_lag) {
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
        }else if(check_lag){
            console.log('STREAM_LAG -> ', new Date().getTime());
        }

        if (!this._finished && this._finishedLoading && this.cache.length < byteLength) {
            this.finish();
            if (this.OnStreamEnd !== Function) {
                this.OnStreamEnd();
            }
            this.emit('finish');
        }
        let time_remove = new Date().getTime() - old_time
        setTimeout(() => this.processData(), (this._finished || this._paused || this.check_lag() ? 500 : 10 ) - time_remove);
    }
}
