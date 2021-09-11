import {createReadStream, ReadStream, statSync} from "fs";
import {EventEmitter} from "events";

export class FileReader extends EventEmitter {
    private readable?:ReadStream;
    constructor(
        readonly path: string,
    ) {
        super();
        this.readable = createReadStream(path);
         this.readable.on('data', (data: any) => {
             this.emit('data', data);
         });
         this.readable.on('end', () => {
             this.emit('end');
         });
    }
    public pause(){
        this.readable?.pause();
    }
    public resume(){
        this.readable?.resume();
    }
    public fileSize(){
         return statSync(this.path).size;
    }
    public stop(){
        this.readable?.destroy();
    }
}
