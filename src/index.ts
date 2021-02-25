import { EventEmitter } from 'events';
import { RTCPeerConnection } from 'wrtc';
import { SdpBuilder } from './sdp-builder';
import { parseSdp } from './utils';
import { JoinVoiceCallCallback } from './types';

export { Stream } from './stream';

export class TGCalls<T> extends EventEmitter {
    #connection?: RTCPeerConnection;
    #params: T;
    #source_id = 0;
    joinVoiceCall?: JoinVoiceCallCallback<T>;

    constructor(params: T) {
        super();
        this.#params = params;
    }

    async start(track: MediaStreamTrack): Promise<boolean> {
        if (this.#connection) {
            throw new Error('Connection already started');
        } else if (!this.joinVoiceCall) {
            throw new Error('Please set the `joinVoiceCall` callback before calling `start()`');
        }

        this.#connection = new RTCPeerConnection();
        this.#connection.oniceconnectionstatechange = async () => {
            this.emit('iceConnectionState', this.#connection?.iceConnectionState);

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

        this.#source_id = source;

        const { transport } = await this.joinVoiceCall({
            ufrag,
            pwd,
            hash,
            setup: 'active',
            fingerprint,
            source,
            params: this.#params,
        });

        if (transport === null) {
            this.#connection.close();
            throw new Error('No transport found');
        }

        const sessionId = Date.now();
        const conference = {
            sessionId,
            transport,
            ssrcs: [{ ssrc: source, isMain: true }],
        };

        await this.#connection.setRemoteDescription({
            type: 'answer',
            sdp: SdpBuilder.fromConference(conference, true),
        });

        return true;
    }

    getSignSource() {
        return this.#source_id;
    }

    close() {
        this.#connection?.close();
        this.#connection = undefined;
    }
}
