import { EventEmitter } from 'events';
const fs = require('fs');
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
    private _path_file = undefined;
    private _bytes_loaded = 0;
    private _bytes_speed = 0;
    private _last_lag = 0;
    private _equal_count = 0;
    private _last_bytes_loaded = 0;
    private _finished_bytes = false;
    private _last_byte_check = 0;
    private _last_byte = 0;

    constructor(
        path_file: any,
        readonly bitsPerSample = 16,
        readonly sampleRate = 48000,
        readonly channelCount = 1,
        readonly log_mode = 0,
        readonly buffer_long = 10,
    ) {
        super();

        this.audioSource = new nonstandard.RTCAudioSource();
        this.cache = Buffer.alloc(0);
        this._path_file = path_file;
        this.setReadable(path_file);
        this.processData();
    }

    setReadable(path_file: any) {
        this._bytes_loaded = 0;
        this._bytes_speed = 0;
        this._last_lag = 0;
        this._equal_count = 0;
        this._last_bytes_loaded = 0;
        this._finished_bytes = false;
        this._last_byte_check = 0;
        this._last_byte = 0;
        this._path_file = path_file;
        // @ts-ignore
        this.local_readable = fs.createReadStream(path_file);
        if (this._stopped) {
            throw new Error('Cannot set readable when stopped');
        }
        this.cache = Buffer.alloc(0);

        if(this.local_readable !== undefined){
            this._finished = false;
            this._finishedLoading = false;

            // @ts-ignore
            this.local_readable.on('data', (data: any) => {
                this._bytes_loaded += data.length;
                this._bytes_speed = data.length;
                if(!this.need_buffering()) {
                    // @ts-ignore
                    this.local_readable.pause();
                    if (this.log_mode > 1) {
                        console.log('ENDED_BUFFERING ->', new Date().getTime());
                        console.log('BYTES_STREAM_CACHE_LENGTH ->', this.cache.length);
                    }
                }
                if (this.log_mode > 1) {
                    // @ts-ignore
                    console.log('BYTES_LOADED ->', this._bytes_loaded, 'OF ->', Stream.getFilesizeInBytes(this._path_file));
                }
                this.cache = Buffer.concat([this.cache, data]);
            });
            // @ts-ignore
            this.local_readable.on('end', () => {
                this._finishedLoading = true;
                if(this.log_mode > 1){
                    console.log('COMPLETED_BUFFERING ->', new Date().getTime());
                    console.log('BYTES_STREAM_CACHE_LENGTH ->', this.cache.length);
                    console.log('BYTES_LOADED ->', this._bytes_loaded, 'OF ->', Stream.getFilesizeInBytes(this._path_file));
                }
            });
        }
    }
    private static getFilesizeInBytes(filename: any) {
        let stats = fs.statSync(filename);
        return stats.size;
    }
    private need_buffering(){
        if(this._finishedLoading){
            return false;
        }
        const byteLength = ((this.sampleRate * this.bitsPerSample) / 8 / 100) * this.channelCount;
        let result_stream = this.cache.length < (byteLength * 100) * this.buffer_long;
        result_stream = result_stream && this._bytes_loaded < Stream.getFilesizeInBytes(this._path_file) - (this._bytes_speed * 2);
        return result_stream || this._finished_bytes;
    }

    private check_lag(){
        if(this._finishedLoading){
            return false;
        }
        const byteLength = ((this.sampleRate * this.bitsPerSample) / 8 / 100) * this.channelCount;
        return this.cache.length < (byteLength * 100) || this._finished_bytes;
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
        if(!this._finishedLoading){
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
            let file_size: number;
            if(old_time - this._last_byte_check > 500){
                file_size = Stream.getFilesizeInBytes(this._path_file);
                this._last_byte = file_size;
                this._last_byte_check = old_time;
            }else{
                file_size = this._last_byte;
            }

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
                if(this.log_mode > 1){
                    console.log('STREAM_LAG -> ', new Date().getTime());
                    console.log('BYTES_STREAM_CACHE_LENGTH ->', this.cache.length);
                    console.log('BYTES_LOADED ->', this._bytes_loaded, 'OF ->', file_size);
                }
            }
            if(file_size === this._last_bytes_loaded){
                if(this._equal_count >= 7){
                    this._equal_count = 0;
                    if(this.log_mode > 1){
                        console.log('NOT_ENOUGH_BYTES ->', old_time);
                    }
                    this._finished_bytes = true;
                }else{
                    if(old_time - this._last_lag > 1000){
                        this._equal_count += 1;
                        this._last_lag = old_time;
                    }
                }
            }else{
                this._last_bytes_loaded = file_size;
                this._equal_count = 0;
                this._finished_bytes = false;
            }
        }
        if (!this._finished && this._finishedLoading) {
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
