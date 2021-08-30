import { EventEmitter } from 'events';
import { RTCPeerConnection } from 'wrtc';
import { SdpBuilder } from './sdp-builder';
import { parseSdp } from './utils';
import { JoinVoiceCallCallback } from './types';

export { Stream } from './stream';

export class TGCalls<T> extends EventEmitter {
    #connection?: RTCPeerConnection;
    readonly #params: any;
    private track?: MediaStreamTrack;
    joinVoiceCall?: JoinVoiceCallCallback<T>;

    constructor(params: T) {
        super();
        this.#params = params;
    }

    async start(track: MediaStreamTrack): Promise<boolean> {
        if (this.#connection) {
            throw new Error('Connection already started');
        } else if (!this.joinVoiceCall) {
            throw new Error(
                'Please set the `joinVoiceCall` callback before calling `start()`',
            );
        }

        this.#connection = new RTCPeerConnection();
        this.#connection.oniceconnectionstatechange = async () => {
            this.emit(
                'iceConnectionState',
                this.#connection?.iceConnectionState,
            );

            switch (this.#connection?.iceConnectionState) {
                case 'closed':
                case 'failed':
                    this.emit('hangUp');
                    break;
            }
        };

        this.track = track;
        this.#connection.addTrack(this.track);
        //this.#connection.addTrack(track2);

        const offer = await this.#connection.createOffer({
            offerToReceiveVideo: false,
            offerToReceiveAudio: true,
        });

        await this.#connection.setLocalDescription(offer);

        if (!offer.sdp) {
            return false;
        }

        const { ufrag, pwd, hash, fingerprint, source } = parseSdp(offer.sdp);

        if (!ufrag || !pwd || !hash || !fingerprint || !source) {
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
                source,
                params: this.#params,
            });
        } catch (error) {
            console.log(error);
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
            ssrcs: [{ ssrc: source, isMain: true }],
        };
        await this.#connection.setRemoteDescription({
            type: 'answer',
            sdp: SdpBuilder.fromConference(conference, true),
        });
        return true;
    }

    mute() {
        if (this.track && this.track.enabled) {
            this.track.enabled = false;
            return true;
        }

        return false;
    }

    unmute() {
        if (this.track && !this.track.enabled) {
            this.track.enabled = true;
            return true;
        }

        return false;
    }

    close() {
        this.#connection?.close();
        this.#connection = undefined;
    }
}
