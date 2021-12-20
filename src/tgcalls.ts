import { EventEmitter } from 'events';
import { RTCPeerConnection } from 'wrtc';
import { SdpBuilder } from './sdp-builder';
import { parseSdp } from './utils';
import { JoinVoiceCallCallback } from './types';
import {Binding} from "./binding";

export { Stream } from './stream';

export class TGCalls<T> extends EventEmitter {
    #connection?: RTCPeerConnection;
    readonly #params: any;
    private audioTrack?: MediaStreamTrack;
    private videoTrack?: MediaStreamTrack;
    private readonly defaultMaxClientRetries: number = 10;
    joinVoiceCall?: JoinVoiceCallCallback<T>;

    constructor(params: T) {
        super();
        this.#params = params;
    }

    async sleep(ms: number) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async start(audioTrack: MediaStreamTrack, videoTrack: MediaStreamTrack, maxRetries: number = this.defaultMaxClientRetries): Promise<boolean> {
        if (this.#connection) {
            throw new Error('Connection already started');
        } else if (!this.joinVoiceCall) {
            throw new Error(
                'Please set the `joinVoiceCall` callback before calling `start()`',
            );
        }
        let resolveConnection: CallableFunction;
        let alreadySolved: boolean = false;
        let resultSolve: boolean = false;
        this.#connection = new RTCPeerConnection();
        this.#connection.oniceconnectionstatechange = async () => {
            const connection_status = this.#connection?.iceConnectionState;
            if(connection_status){
                this.emit(
                    'iceConnectionState',
                    connection_status,
                );
                const isConnected = connection_status == 'completed' || connection_status == 'connected';
                if(connection_status != 'checking'){
                    if(resolveConnection){
                        resolveConnection(isConnected);
                    }else{
                        alreadySolved = true;
                        resultSolve = isConnected;
                    }
                }
                switch (connection_status) {
                    case 'closed':
                    case 'failed':
                        this.emit('hangUp');
                        break;
                }
            }
        };

        this.audioTrack = audioTrack;
        this.#connection.addTrack(this.audioTrack);
        this.videoTrack = videoTrack;
        this.#connection.addTrack(this.videoTrack);

        const offer = await this.#connection.createOffer({
            offerToReceiveVideo: true,
            offerToReceiveAudio: true,
        });

        await this.#connection.setLocalDescription(offer);
        if (!offer.sdp) {
            return false;
        }
        const { ufrag, pwd, hash, fingerprint, audioSource, source_groups} = parseSdp(offer.sdp);

        if (!ufrag || !pwd || !hash || !fingerprint || !audioSource || !source_groups) {
            return false;
        }

        let joinGroupCallResult;
        try {
            //The setup need to be active
            joinGroupCallResult = await this.joinVoiceCall({
                ufrag,
                pwd,
                hash,
                setup: 'active',
                fingerprint,
                source: audioSource,
                source_groups: source_groups,
                params: this.#params,
            });
        } catch (error: any) {
            Binding.log(error.toString(), Binding.ERROR);
            this.#connection.close();
            throw error;
        }

        if (!joinGroupCallResult || !joinGroupCallResult.transport) {
            this.#connection.close();
            throw new Error(
                'No active voice chat found on ' + this.#params.chatId,
            );
        }

        const session_id = Date.now();
        const conference = {
            session_id,
            transport: joinGroupCallResult.transport,
            ssrcs: [
                {
                    ssrc: audioSource,
                    ssrc_group: source_groups,
                },
            ],
        };
        await this.#connection.setRemoteDescription({
            type: 'answer',
            sdp: SdpBuilder.fromConference(conference),
        });
        let result_connection: boolean;
        if(alreadySolved){
            result_connection = resultSolve;
        }else{
            result_connection = await new Promise<boolean>(resolve => {
                resolveConnection = resolve;
            });
        }
        if(result_connection){
            return result_connection;
        }else{
            if(maxRetries > 0){
                try{
                    this.#connection.close();
                }catch (e){}
                this.#connection = undefined;
                await this.sleep(125);
                Binding.log('Telegram is having some internal server problems! Retrying ' + ((this.defaultMaxClientRetries + 1) - maxRetries) + ' of ' + this.defaultMaxClientRetries, Binding.WARNING);
                return await this.start(audioTrack, videoTrack, maxRetries - 1);
            }else{
                return result_connection;
            }
        }
    }

    mute() {
        if (this.audioTrack && this.audioTrack.enabled) {
            this.audioTrack.enabled = false;
            return true;
        }

        return false;
    }

    unmute() {
        if (this.audioTrack && !this.audioTrack.enabled) {
            this.audioTrack.enabled = true;
            return true;
        }

        return false;
    }

    isClosed(){
        return this.#connection?.connectionState == 'closed';
    }

    close() {
        this.#connection?.close();
        this.#connection = undefined;
    }
}
