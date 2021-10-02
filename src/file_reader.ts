import {createReadStream, ReadStream, statSync} from "fs";
import {onData, onEnd} from "./types";

export class FileReader {
    private readable?:ReadStream;
    public haveEnd: boolean = true;
    onData?: onData;
    onEnd?: onEnd;

    constructor(
        readonly path: string,
    ) {
        this.readable = createReadStream(path);
        this.readable.on('data', (data: any) => {
            if(this.onData != undefined){
                this.onData(data);
            }
        });
        this.readable.on('end', () => {
            if(this.onEnd != undefined){
                this.onEnd();
            }
        });
        this.readable?.pause();
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
        this.readable?.pause();
        this.readable?.destroy();
    }
}
