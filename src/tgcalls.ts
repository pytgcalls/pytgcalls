import { EventEmitter } from 'events';
import { RTCPeerConnection } from 'wrtc';
import { SdpBuilder } from './sdp-builder';
import { parseSdp } from './utils';
import { JoinVoiceCallCallback } from './types';

export { Stream } from './stream';

export class TGCalls<T> extends EventEmitter {
    #connection?: RTCPeerConnection;
    readonly #params: any;
    private audioTrack?: MediaStreamTrack;
    private videoTrack?: MediaStreamTrack;
    joinVoiceCall?: JoinVoiceCallCallback<T>;

    constructor(params: T) {
        super();
        this.#params = params;
    }

    async start(audioTrack: MediaStreamTrack, videoTrack?: MediaStreamTrack): Promise<boolean> {
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

        this.audioTrack = audioTrack;
        this.#connection.addTrack(this.audioTrack);
        if(videoTrack !== undefined){
            this.videoTrack = videoTrack;
            this.#connection.addTrack(this.videoTrack);
        }

        const offer = await this.#connection.createOffer({
            offerToReceiveVideo: videoTrack !== undefined,
            offerToReceiveAudio: true,
        });

        await this.#connection.setLocalDescription(offer);
        if (!offer.sdp) {
            return false;
        }
        const { ufrag, pwd, hash, fingerprint, audioSource, source_groups} = parseSdp(offer.sdp);

        if (!ufrag || !pwd || !hash || !fingerprint || !audioSource) {
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
            ssrcs: [
                {
                    ssrc: audioSource,
                    isMain: true,
                    ssrc_group: source_groups == null ? undefined:source_groups
                },
            ],
        };
        await this.#connection.setRemoteDescription({
            type: 'answer',
            sdp: SdpBuilder.fromConference(conference, true),
        });
        return true;
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

    close() {
        this.#connection?.close();
        this.#connection = undefined;
    }
}
