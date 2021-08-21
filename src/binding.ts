import { EventEmitter } from 'events';

export class Binding extends EventEmitter{
    private is_connected: boolean;
    private readonly ssid: string;
    private readonly list_promise: any;
    static DEBUG: number = 1;
    static INFO: number = 2;
    static WARNING: number = 3;
    static ERROR: number = 4;
    constructor() {
        super();
        this.is_connected = false;
        this.ssid = '0';
        this.list_promise = [];
        process.stdin.on('data', (chunk: boolean) => {
            try {
                let data = JSON.parse(chunk.toString());
                if(data.try_connect == 'connected') {
                    this.is_connected = true;
                    Binding.sendUpdateInternal({
                        ping: true
                    })
                    setInterval(function () {
                        Binding.sendUpdateInternal({
                            ping: true
                        })
                    }, 10000)
                    this.emit('connect', data.user_id);
                }else if(data.ping_with_response){
                     Binding.sendUpdateInternal({
                        ping_with_response: true
                    })
                }else if(data.ssid == this.ssid){
                    if (data.uid !== undefined){
                        if(this.list_promise[data.uid] !== undefined){
                            if(data.data !== undefined){
                                this.list_promise[data.uid](data.data);
                            }else{
                                this.list_promise[data.uid](null);
                            }
                        }
                    }else{
                        this.emit('request', data.data);
                    }
                }
            }catch(e){}
        });
        this.ssid = Binding.makeID(12);
        Binding.sendUpdateInternal({
            try_connect: this.ssid
        })
    }
    async sendUpdate(update: any): Promise<any>{
        if(this.is_connected){
            let uid = Binding.makeID(12);
            Binding.sendUpdateInternal({
                data: update,
                uid: uid,
                ssid: this.ssid
            });
            return new Promise((resolve) => {
                this.list_promise[uid] = (data: any) => {
                    resolve(data)
                    delete this.list_promise[uid]
                }
            })
        }else{
            throw new Error('No connected client');
        }
    }
    static log(message: string, verbose_mode: number){
        Binding.sendUpdateInternal({
            log_message: message,
            verbose_mode: verbose_mode,
        })
    }
    private static makeID(length: number): string {
        let result           = '';
        let characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let charactersLength = characters.length;
        for (let i = 0; i < length; i++ ) {
            result += characters.charAt(Math.floor(Math.random() * charactersLength));
        }
        return result;
    }

    private static sendUpdateInternal(update: any){
        console.log(JSON.stringify(update))
    }
}
