import { EventEmitter } from 'events';
import { RTCPeerConnection } from 'wrtc';
import { SdpBuilder } from './sdp-builder';
import { parseSdp } from './utils';
import { JoinVoiceCallCallback } from './types';

export { Stream } from './stream';

export class TGCalls<T> extends EventEmitter {
    #connection?: RTCPeerConnection;
    #params: T;
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
                'Please set the `joinVoiceCall` callback before calling `start()`'
            );
        }

        this.#connection = new RTCPeerConnection();
        this.#connection.oniceconnectionstatechange = async () => {
            this.emit(
                'iceConnectionState',
                this.#connection?.iceConnectionState
            );

            switch (this.#connection?.iceConnectionState) {
                case 'closed':
                case 'failed':
                    this.emit('hangUp');
                    break;
            }
        };

        this.#connection.addTrack(track);

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
            this.#connection.close();
            throw error;
        }

        if (!joinGroupCallResult || !joinGroupCallResult.transport) {
            this.#connection.close();
            throw new Error('No transport found');
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

    close() {
        this.#connection?.close();
        this.#connection = undefined;
    }
}
