import {ChildProcessWithoutNullStreams, spawn} from 'child_process';
import {EventEmitter} from "events";

export class FFmpegReader extends EventEmitter {
    private fifo_reader?: ChildProcessWithoutNullStreams;
    private readonly promises = new Map<string, CallableFunction>();
    private readonly CURRENT_PATH = __dirname.replace('dist', '');
    private readonly FIFO_PATH = this.CURRENT_PATH + 'custom_fifo/mkfifo.py';
    private offlineFileSize: number = 0;

    public convert_video(path: string, resolution: string, framerate: string){
        this.start_conversion([
            this.FIFO_PATH,
            path.replace('fifo://', ''),
            'video',
            resolution,
            framerate,
        ])
    }
    public convert_audio(path: string, bitrate: string){
        this.start_conversion([
            this.FIFO_PATH,
            path.replace('fifo://', ''),
            'audio',
            bitrate,
        ])
    }
    private start_conversion(params: Array<string>){
        this.fifo_reader = spawn('python3.8', params);
        if(this.fifo_reader !== undefined){
            this.fifo_reader.stdout.on('data', (data: any) => {
                this.emit('data', data);
            });
            this.fifo_reader.stderr.on('data', (chunk: any) => {
                const list_data = chunk.toString().split('}{').join('}\n{').split('\n');
                try {
                    for(let i = 0; i < list_data.length; i++) {
                        const data = JSON.parse(list_data[i]);
                        if(data.result == 'GET_FILE_SIZE'){
                            if (data.uid !== undefined) {
                                const promise = this.promises.get(data.uid);
                                if (promise) {
                                    if (data.data !== undefined) {
                                        promise(data.data);
                                    }else{
                                        promise(null);
                                    }
                                }
                            }
                        }else if(data.result == 'ENDED'){
                            this.offlineFileSize = parseInt(data.file_size);
                            this.emit('end');
                        }
                    }
                }catch (e){
                }
            });
        }

    }
    public pause(){
        if(this.fifo_reader !== undefined){
            this.fifo_reader.stdin.write(JSON.stringify({
                'request': 'PAUSE',
            }) + '\n');
        }
    }
    public resume(){
        if(this.fifo_reader !== undefined){
            this.fifo_reader.stdin.write(JSON.stringify({
                'request': 'RESUME',
            }) + '\n');
        }
    }
    public async fileSize(){
        if(this.fifo_reader !== undefined){
            if(this.offlineFileSize > 0){
                return this.offlineFileSize;
            }
            const uid = FFmpegReader.makeID(12);
            this.fifo_reader.stdin.write(JSON.stringify({
                'request': 'GET_FILE_SIZE',
                'uid': uid,
            }) + '\n');
            return new Promise(resolve => {
                this.promises.set(uid, (data: any) => {
                    resolve(data);
                    this.promises.delete(uid);
                });
            });
        }else{
            return 0;
        }
    }
    private static makeID(length: number): string {
        const characters =
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';
        for (let i = 0; i < length; i++) {
            result += characters.charAt(
                Math.floor(Math.random() * characters.length),
            );
        }
        return result;
    }
    public stop(){
        this.fifo_reader?.kill()
    }
}
