export class BufferOptimized{
    private buffer: Array<Buffer> = [];
    length: number = 0;
    byteLength: number = 0;
    constructor(byteLength: number) {
        this.byteLength = byteLength;
    }
    push(data: Buffer){
        this.buffer.push(data);
        this.length += data.byteLength;
    }
    readBytes(){
        let buffer = Buffer.alloc(this.byteLength);
        let chunkSize = 0;
        this.buffer.find((chunk, i) => {
            if (chunkSize === 0) {
                chunk.copy(buffer, 0, 0, this.byteLength);
                chunkSize = Math.min(chunk.length, this.byteLength);
                this.buffer[i] = chunk.slice(this.byteLength);
            } else {
                let req = this.byteLength - chunkSize;
                let tmpChunk: Buffer;
                tmpChunk = req < chunk.length ? chunk.slice(0, req) : chunk;
                tmpChunk.copy(buffer, chunkSize);
                chunkSize += tmpChunk.length;
                this.buffer[i] = chunk.slice(req);
            }
            return chunkSize >= this.byteLength;
        });
        this.length -= this.byteLength;
        this.buffer.splice(
            0,
            this.buffer.findIndex(i => i.length),
        );
        return buffer;
    }
}
