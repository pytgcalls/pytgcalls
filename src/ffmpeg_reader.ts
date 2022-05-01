import {ChildProcessWithoutNullStreams, spawn} from 'child_process';
import { onData, onEnd } from './types';
import {Binding} from "./binding";
import {BufferOptimized} from "./buffer_optimized";
import {getBuiltCommands} from "./utils";

export class FFmpegReader {
    private fifo_reader?: ChildProcessWithoutNullStreams;
    private total_size: number = 0;
    private bytes_read: BufferOptimized;
    private MAX_READ_BUFFER: number = 65536 * 4;
    private MAX_SIZE_BUFFERED: number = 5 * this.MAX_READ_BUFFER;
    private paused: boolean = true;
    private stopped: boolean = false;
    private readonly additional_parameters: string = '';
    private almostFinished: boolean = false;
    public haveEnd: boolean = true;
    private isLiveSharing: boolean = false;
    onData?: onData;
    onEnd?: onEnd;

    constructor(additional_parameters: string) {
        this.bytes_read = new BufferOptimized(0);
        this.additional_parameters = additional_parameters;
    }
    public convert_audio(path: string, bitrate: string){
        let cmds = getBuiltCommands(this.additional_parameters);
        this.isLiveSharing = path.startsWith('device://');
        this.start_conversion(cmds.audio.before.concat([
            '-i',
            path.replace('fifo://', '').replace('device://', ''),
        ]).concat(cmds.audio.middle).concat([
            '-f',
            's16le',
            '-ac',
            '1',
            '-ar',
            bitrate,
            'pipe:1',
        ]).concat(cmds.audio.after));
    }
    public convert_video(path: string, width: string, height: string, framerate: string){
       let cmds = getBuiltCommands(this.additional_parameters);
       if(path.includes('image:')){
           cmds.video.before.concat([
               '-loop',
               '1',
               '-framerate',
               '1'
           ])
           this.haveEnd = false;
       }
       this.isLiveSharing = path.startsWith('screen://');
       this.start_conversion(cmds.video.before.concat([
           '-i',
           path.replace('fifo://', '').replace('screen://', '').replace('image:', ''),
       ]).concat(cmds.video.middle).concat([
           '-f',
           'rawvideo',
           '-pix_fmt',
           'yuv420p',
           '-r',
           framerate,
           '-vf',
           'scale=' + width + ':' + height,
           'pipe:1',
       ]).concat(cmds.video.after));
    }
    private start_conversion(params: Array<string>) {
        params = params.filter(e => e);
        Binding.log('RUNNING_FFMPEG_COMMAND -> ffmpeg ' + params.join(' '), Binding.INFO);
        this.fifo_reader = spawn('ffmpeg', params);
        this.fifo_reader.stdout.on('data', this.dataListener);
        this.fifo_reader.stderr.on('data', async (chunk: any) => {
            const message = chunk.toString();
            if (message.includes('] Opening')){
                Binding.log('OPENING_M3U8_SOURCE -> ' + (new Date().getTime()), Binding.DEBUG);
            } else if (message.includes('] Unable')) {
                let list_err = message.split('\n');
                for(let i = 0; i < list_err.length; i++){
                    if(list_err[i].includes('] Unable')){
                        Binding.log(list_err[i], Binding.ERROR);
                        break;
                    }
                }
            }
        });
        this.fifo_reader.on('close', this.endListener);
        this.processBytes();
    }
    private dataListener = (async (chunk: any) => {
        this.total_size += chunk.length;
        this.bytes_read.push(chunk);
        if(this.bytes_read.length >= this.MAX_SIZE_BUFFERED && !this.isLiveSharing){
            this.fifo_reader?.stdout.pause();
        }
    });
    private endListener = (async () => {
        this.almostFinished = true;
    });
    private processBytes(){
        const oldTime = new Date().getTime();
        if(this.stopped){
            return;
        }
        if(!this.paused){
            if(this.bytes_read.length > 0){
                if(this.bytes_read.length < this.MAX_SIZE_BUFFERED && !this.isLiveSharing){
                    this.fifo_reader?.stdout.resume();
                }
                this.bytes_read.byteLength = this.bytes_read.length < this.MAX_READ_BUFFER ? this.bytes_read.length:this.MAX_READ_BUFFER;
                if(this.onData != undefined){
                    const buffer = this.bytes_read.readBytes();
                    this.onData(buffer);
                }
            }else if(this.almostFinished){
                if(this.onEnd != undefined){
                    this.onEnd();
                }
                this.fifo_reader?.kill()
                return;
            }
        }
        const toSubtract = new Date().getTime() - oldTime;
        setTimeout(
            async () => this.processBytes(),
            5 - toSubtract,
        );
    }
    public pause(){
        this.paused = true;
    }
    public resume(){
        this.paused = false;
    }
    public fileSize(){
        return this.total_size;
    }
    public stop(){
        this.fifo_reader?.stdout.removeListener('data', this.dataListener);
        this.fifo_reader?.removeListener('close', this.endListener);
        this.stopped = true;
        this.fifo_reader?.stdout.pause();
        this.fifo_reader?.kill('SIGKILL');
    }
}
