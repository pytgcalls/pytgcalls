import {ChildProcessWithoutNullStreams, spawn} from 'child_process';
import { onData, onEnd } from './types';
import {Binding} from "./binding";

export class FFmpegReader {
    private fifo_reader?: ChildProcessWithoutNullStreams;
    private total_size: number = 0;
    private bytes_read: Buffer;
    private MAX_READ_BUFFER: number = 65536 * 4;
    private MAX_SIZE_BUFFERED: number = 5 * this.MAX_READ_BUFFER;
    private paused: boolean = true;
    private stopped: boolean = false;
    private readonly additional_parameters: string = '';
    private almostFinished: boolean = false;
    onData?: onData;
    onEnd?: onEnd;

    constructor(additional_parameters: string) {
        this.bytes_read = Buffer.alloc(0);
        this.additional_parameters = additional_parameters.includes('-atend') ? additional_parameters:additional_parameters + '-atend';
    }
    public convert_audio(path: string, bitrate: string){
        let list_cmd = this.additional_parameters.split('-atend');
        this.start_conversion(this.parse_cmdline(list_cmd[0]).concat([
            '-i',
            path.replace('fifo://', ''),
            '-f',
            's16le',
            '-ac',
            '1',
            '-ar',
            bitrate,
            'pipe:1',
        ]).concat(this.parse_cmdline(list_cmd[1])));
    }
    public convert_video(path: string, resolution: string, framerate: string){
       let list_cmd = this.additional_parameters.split('-atend');
       this.start_conversion(this.parse_cmdline(list_cmd[0]).concat([
            '-i',
            path.replace('fifo://', ''),
            '-f',
            'rawvideo',
            '-r',
            framerate,
            '-vf',
            'scale=' + resolution + ':-1',
            'pipe:1',
        ]).concat(this.parse_cmdline(list_cmd[1])));
    }
    private start_conversion(params: Array<string>) {
        params = params.filter(e =>  e);
        this.fifo_reader = spawn('ffmpeg', params);
        this.fifo_reader.stdout.on('data', this.dataListener);
        this.fifo_reader.stderr.on('data', async (chunk: any) => {
            const message = chunk.toString();
            if(message.includes('] Opening')){
                Binding.log('OPENING_M3U8_SOURCE -> ' + (new Date().getTime()), Binding.DEBUG);
            }else if (message.includes('] Unable')) {
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
        this.bytes_read = Buffer.concat([this.bytes_read, chunk]);
        if(this.bytes_read.length >= this.MAX_SIZE_BUFFERED){
            this.fifo_reader?.stdout.pause();
        }
    });
    parse_cmdline(cmdline: string) {
        let re_next_arg = /^\s*((?:(?:"(?:\\.|[^"])*")|(?:'[^']*')|\\.|\S)+)\s*(.*)$/;
        let next_arg = ['', '', cmdline];
        let args = [];
        // @ts-ignore
        while (next_arg = re_next_arg.exec(next_arg[2])) {
            let quoted_arg = next_arg[1];
            let unquoted_arg = "";
            while (quoted_arg.length > 0) {
                if (/^"/.test(quoted_arg)) {
                    let quoted_part = /^"((?:\\.|[^"])*)"(.*)$/.exec(quoted_arg);
                    if (quoted_part) {
                        unquoted_arg += quoted_part[1].replace(/\\(.)/g, "$1");
                    }
                    if (quoted_part) {
                        quoted_arg = quoted_part[2];
                    }
                } else if (/^'/.test(quoted_arg)) {
                    let quoted_part = /^'([^']*)'(.*)$/.exec(quoted_arg);
                    if (quoted_part) {
                        unquoted_arg += quoted_part[1];
                    }
                    if (quoted_part) {
                        quoted_arg = quoted_part[2];
                    }
                } else if (/^\\/.test(quoted_arg)) {
                    unquoted_arg += quoted_arg[1];
                    quoted_arg = quoted_arg.substring(2);
                } else {
                    unquoted_arg += quoted_arg[0];
                    quoted_arg = quoted_arg.substring(1);
                }
            }
            args[args.length] = unquoted_arg;
        }
        return args;
    }
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
                if(this.bytes_read.length < this.MAX_SIZE_BUFFERED){
                    this.fifo_reader?.stdout.resume();
                }
                const buffer_length = this.bytes_read.length < this.MAX_READ_BUFFER ? this.bytes_read.length:this.MAX_READ_BUFFER;
                const buffer = this.bytes_read.slice(0, buffer_length);
                if(this.onData != undefined){
                    this.onData(buffer);
                    this.bytes_read = this.bytes_read.slice(buffer_length);
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
