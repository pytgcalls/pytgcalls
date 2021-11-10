import { EventEmitter } from 'events';
import * as process from "process";

export class Binding extends EventEmitter {
    private connected = false;
    public overload_quiet = false;
    public multi_thread = false;
    private readonly ssid: string;
    private readonly promises = new Map<string, CallableFunction>();
    private readonly listPendingUpdates = new Map<number, Map<string, any>>();
    private readonly activeUpdates = new Map<number, boolean>();
    static DEBUG = 1;
    static INFO = 2;
    static WARNING = 3;
    static ERROR = 4;

    constructor() {
        super();
        process.stdin.on('data', (chunk: boolean) => {
            try {
                const list_data = chunk.toString().split('}{').join('}\n{').split('\n');
                for(let i = 0; i < list_data.length; i++){
                    const data = JSON.parse(list_data[i]);
                    if (data.try_connect == 'connected') {
                        this.connected = true;
                        this.overload_quiet = data.overload_quiet;
                        this.multi_thread = data.multi_thread;
                        Binding.sendInternalUpdate({
                            ping: true,
                        });
                        setInterval(
                            () =>
                                Binding.sendInternalUpdate({
                                    ping: true,
                                }),
                            10000,
                        );
                        setInterval(
                            () => {
                                this.listPendingUpdates.forEach((value, chat_id) => {
                                        value.forEach((update_saved, update_id) => {
                                            if(!this.activeUpdates.get(chat_id)){
                                                this.activeUpdates.set(
                                                    chat_id,
                                                    true,
                                                );
                                                this.emit('request', update_saved, update_id);
                                            }
                                        });
                                    }
                                );
                            }, 50
                        );
                        this.emit('connect', data.user_id);
                    } else if (data.ping_with_response) {
                        Binding.sendInternalUpdate({
                            ping_with_response: true,
                            sid: data.sid,
                        });
                    } else if (data.ssid == this.ssid) {
                        if (data.uid !== undefined) {
                            const promise = this.promises.get(data.uid);
                            if (promise) {
                                if (data.data !== undefined) {
                                    promise(data.data);
                                } else {
                                    promise(null);
                                }
                            }
                        } else {
                            this.appendUpdate(data.data);
                        }
                    }
                }

            } catch (e) {
                console.log(e);
                Binding.log('Invalid Binding Update', Binding.ERROR);
            }
        });
        this.ssid = Binding.makeID(12);
        Binding.sendInternalUpdate({
            try_connect: this.ssid,
        });
    }

    private appendUpdate(update: any){
        const chat_id = update.chat_id;
        let pending_updates = this.listPendingUpdates.get(
            chat_id,
        )
        const updateID = Binding.makeID(12);
        if(!pending_updates){
            pending_updates = new Map<string, any>();
            pending_updates.set(
                updateID,
                update,
            )
            this.listPendingUpdates.set(
                chat_id,
                pending_updates,
            )
        }else{
            pending_updates.set(
                updateID,
                update,
            )
        }
    }

    resolveUpdate(chat_id: number, update_id: string){
        let pending_updates = this.listPendingUpdates.get(
            chat_id,
        )
        pending_updates?.delete(update_id);
        if(pending_updates?.size == 0){
            this.listPendingUpdates.delete(
                chat_id,
            )
        }
        this.activeUpdates.delete(
            chat_id,
        );
    }

    async sendUpdate(update: any): Promise<any> {
        if (this.connected) {
            const uid = Binding.makeID(12);
            Binding.sendInternalUpdate({
                uid,
                data: update,
                ssid: this.ssid,
            });
            return new Promise(resolve => {
                this.promises.set(uid, (data: any) => {
                    resolve(data);
                    this.promises.delete(uid);
                });
            });
        } else {
            throw new Error('No connected client');
        }
    }

    static log(message: string, verbose_mode: number) {
        Binding.sendInternalUpdate({
            log_message: message,
            verbose_mode: verbose_mode,
        });
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

    private static sendInternalUpdate(update: any) {
        console.log(JSON.stringify(update));
    }
}
export class MultiCoreBinding{
    private readonly promises = new Map<string, CallableFunction>();
    constructor(private process_multicore: any) {}
    resolveUpdate(data: any){
        const promise = this.promises.get(data.uid);
        if (promise) {
            if (data.result !== undefined) {
                promise(data.result);
            } else {
                promise(null);
            }
        }
    }
    async sendUpdate(update: any): Promise<any> {
        const uid = MultiCoreBinding.makeID(12);
        this.process_multicore.postMessage({
            action: 'binding_update',
            uid: uid,
            update: update,
        });
        return new Promise(resolve => {
            this.promises.set(uid, (data: any) => {
                resolve(data);
                this.promises.delete(uid);
            });
        });
    }
    private static makeID(length: number): string {
        const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';
        for (let i = 0; i < length; i++) {
            result += characters.charAt(
                Math.floor(Math.random() * characters.length),
            );
        }
        return result;
    }
}
