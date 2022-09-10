import { EventEmitter } from 'events';
import { RTCPeerConnection } from 'wrtc';
import { SdpBuilder } from './sdp-builder';
import {LogLevel, uuid, parseSdp, second, getErrorMessage} from './utils';
import {Conference, JoinVoiceCallCallback, JoinVoiceCallResponse, Sdp} from './types';
import {Binding} from './binding';

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

    private async sleep(ms: number) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    private async checkConnection() {
        if (this.#connection) {
            throw new Error('Connection already started');
        } else if (!this.joinVoiceCall) {
            throw new Error(
                'Please set the `joinVoiceCall` callback before calling `start()`',
            );
        }
    }

    private async setConnectionListener(connection: RTCPeerConnection, resolve: (o: boolean) => void) {
        connection.oniceconnectionstatechange = async () => {
            const connection_status = connection.iceConnectionState;
            if(connection_status) {
                this.emit(
                    'iceConnectionState',
                    connection_status,
                );

                const isConnected = connection_status == 'completed' || connection_status == 'connected';

                if(connection_status != 'checking') {
                    resolve(isConnected)
                }

                switch (connection_status) {
                    case 'closed':
                    case 'failed':
                        this.emit('hangUp');
                        break;
                }
            }
        };
        return connection;
    }

    async start(audioTrack: MediaStreamTrack, videoTrack: MediaStreamTrack, maxRetries: number = this.defaultMaxClientRetries): Promise<void> {
        let resolve: (o: boolean) => void;
        let resolver = new Promise<boolean>(ok => resolve = ok);

        const setConnection = () => this.#connection = new RTCPeerConnection();
        const setListener = (conn: RTCPeerConnection) => this.setConnectionListener(conn, resolve);
        const setAudioTrack = (conn: RTCPeerConnection) => second(this.audioTrack = audioTrack, conn);
        const addAudioTrack = (conn: RTCPeerConnection) => second(conn.addTrack(this.audioTrack!), conn);
        const setVideoTrack = (conn: RTCPeerConnection) => second(this.videoTrack = videoTrack, conn);
        const addVideoTrack = (conn: RTCPeerConnection) => second(conn.addTrack(this.videoTrack!), conn);
        const createOffer = async (conn: RTCPeerConnection) =>
            conn.createOffer({
                offerToReceiveVideo: true,
                offerToReceiveAudio: true
            })
            .then(offer => ({ conn, offer }));
        const setLocalDescription = async ({ conn, offer }: { conn: RTCPeerConnection, offer: RTCSessionDescriptionInit }) =>
            conn.setLocalDescription(offer).then(() => {
                if(!offer.sdp) throw new Error('No offer sdp');
                return offer;
            })
            .then(offer => ({ conn, offer }));
        const setSdp = ({ conn, offer }: { conn: RTCPeerConnection, offer: RTCSessionDescriptionInit }) =>
            ({ conn, offer, parsedSdp: parseSdp(offer.sdp!) });
        const checkSdp = ({ conn, parsedSdp }: { conn: RTCPeerConnection, parsedSdp: Sdp }) => {
            if (!parsedSdp.ufrag
               || !parsedSdp.pwd
               || !parsedSdp.hash
               || !parsedSdp.fingerprint
               || !parsedSdp.audioSource
               || !parsedSdp.source_groups
            ) throw new Error('Invalid SDP');
           return ({ conn, sdp: parsedSdp });
        }
        const joinVoiceCall = async ({ conn, sdp }: { conn: RTCPeerConnection, sdp: Sdp }) => this.joinVoiceCall!({
            ufrag: sdp.ufrag!,
            pwd: sdp.pwd!,
            hash: sdp.hash!,
            fingerprint: sdp.fingerprint!,
            source: sdp.audioSource!,
            source_groups: sdp.source_groups!,
            params: this.#params,
            setup: 'active' //The setup need to be active
        }).catch(e => {
            Binding.log(e.toString(), LogLevel.ERROR);
            conn.close();
            throw e;
        }).then(answer => {
            if(!answer || !answer.transport) {
                conn.close();
                if (answer.error) {
                    const messageError = getErrorMessage(answer.error);
                    if (messageError != 'JOIN_ERROR') {
                        throw new Error(messageError);
                    }
                }
                throw new Error('No active voice chat found on ' + this.#params.chatId);
            }
            else return answer;
        }).then(answer => ({ conn, sdp, answer }))
        const setUUID = ({conn, sdp, answer}: {conn: RTCPeerConnection, sdp: Sdp, answer: JoinVoiceCallResponse}) => ({
            conn,
            answer,
            sdp,
            connId: Number(uuid(8).split('').map(s => s.charCodeAt(0)).join()),
        });
        const setConference = ({conn, answer, sdp, connId}: {conn: RTCPeerConnection, answer: JoinVoiceCallResponse, sdp: Sdp, connId: number}) => ({
            conn,
            answer,
            connId,
            conference: {
                session_id: connId,
                transport: answer.transport!,
                ssrcs: [
                    {
                        ssrc: sdp.audioSource!,
                        ssrc_group: sdp.source_groups!,
                    },
                ]
            }
        })
        const setRemoteDescription = ({conn, conference}: {conn: RTCPeerConnection, conference: Conference}) => second(
            conn.setRemoteDescription({ type: 'answer', sdp: SdpBuilder.fromConference(conference) }), conn
        )
        const waitConnection = (conn: RTCPeerConnection) => resolver.then(isConnected => ({ conn, isConnected }));
        const retryOrDone = async ({ conn, isConnected }: { conn: RTCPeerConnection, isConnected: boolean }) => {
            if(!isConnected) {
                try {
                    conn.close();
                } catch (e) {}
                if(maxRetries > 0) {
                    this.#connection = undefined;
                    await this.sleep(125);
                    Binding.log('Telegram is having some internal server issues. Retrying ' + ((this.defaultMaxClientRetries + 1) - maxRetries) + ' of ' + this.defaultMaxClientRetries, LogLevel.WARNING);
                    return this.start(audioTrack, videoTrack, maxRetries - 1);
                }
                throw new Error('Telegram is having some internal server issues. Retries exhausted');
            }
        }

        return this.checkConnection()
            .then(setConnection)
            .then(setListener)
            .then(setAudioTrack)
            .then(addAudioTrack)
            .then(setVideoTrack)
            .then(addVideoTrack)
            .then(createOffer)
            .then(setLocalDescription)
            .then(setSdp)
            .then(checkSdp)
            .then(joinVoiceCall)
            .then(setUUID)
            .then(setConference)
            .then(setRemoteDescription)
            .then(waitConnection)
            .then(retryOrDone);
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
