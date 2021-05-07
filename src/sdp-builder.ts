import { Candidate, Conference, Ssrc, Transport } from './types';

export class SdpBuilder {
    #lines: string[] = [];
    #newLine: string[] = [];

    get lines() {
        return this.#lines.slice();
    }

    join() {
        return this.#lines.join('\n');
    }

    finalize() {
        return this.join() + '\n';
    }

    private add(line: string) {
        this.#lines.push(line);
    }

    private push(word: string) {
        this.#newLine.push(word);
    }

    private addJoined(separator = '') {
        this.add(this.#newLine.join(separator));
        this.#newLine = [];
    }

    addCandidate(c: Candidate) {
        this.push('a=candidate:');
        this.push(
            `${c.foundation} ${c.component} ${c.protocol} ${c.priority} ${c.ip} ${c.port} typ ${c.type}`
        );

        if ('rel-addr' in c) {
            this.push(` raddr ${c['rel-addr']} rport ${c['rel-port']}`);
        }

        this.push(` generation ${c.generation}`);
        this.addJoined();
    }

    addHeader(session_id: number, ssrcs: Ssrc[]) {
        this.add('v=0');
        this.add(`o=- ${session_id} 2 IN IP4 0.0.0.0`);
        this.add('s=-');
        this.add('t=0 0');
        this.add(`a=group:BUNDLE ${ssrcs.map(this.toAudioSsrc).join(' ')}`);
        this.add('a=ice-lite');
    }

    addTransport(transport: Transport) {
        this.add(`a=ice-ufrag:${transport.ufrag}`);
        this.add(`a=ice-pwd:${transport.pwd}`);

        for (let fingerprint of transport.fingerprints) {
            this.add(
                `a=fingerprint:${fingerprint.hash} ${fingerprint.fingerprint}`
            );
            this.add(`a=setup:passive`);
        }

        let candidates = transport.candidates;
        for (let candidate of candidates) {
            this.addCandidate(candidate);
        }
    }

    addSsrcEntry(entry: Ssrc, transport: Transport, isAnswer: boolean) {
        let ssrc = entry.ssrc;

        this.add(`m=audio ${entry.isMain ? 1 : 0} RTP/SAVPF 111 126`);

        if (entry.isMain) {
            this.add('c=IN IP4 0.0.0.0');
        }

        this.add(`a=mid:${this.toAudioSsrc(entry)}`);

        if (entry.isRemoved) {
            this.add('a=inactive');
            return;
        }

        if (entry.isMain) {
            this.addTransport(transport);
        }

        this.add('a=rtpmap:111 opus/48000/2');
        this.add('a=rtpmap:126 telephone-event/8000');
        this.add('a=fmtp:111 minptime=10; useinbandfec=1; usedtx=1');
        this.add('a=rtcp:1 IN IP4 0.0.0.0');
        this.add('a=rtcp-mux');
        this.add('a=rtcp-fb:111 transport-cc');
        this.add('a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level');

        if (isAnswer) {
            this.add('a=recvonly');
            return;
        } else if (entry.isMain) {
            this.add('a=sendrecv');
        } else {
            this.add('a=sendonly');
            this.add('a=bundle-only');
        }

        this.add(`a=ssrc-group:FID ${ssrc}`);
        this.add(`a=ssrc:${ssrc} cname:stream${ssrc}`);
        this.add(`a=ssrc:${ssrc} msid:stream${ssrc} audio${ssrc}`);
        this.add(`a=ssrc:${ssrc} mslabel:audio${ssrc}`);
        this.add(`a=ssrc:${ssrc} label:audio${ssrc}`);
    }

    addConference(conference: Conference, isAnswer = false) {
        let ssrcs = conference.ssrcs;

        if (isAnswer) {
            for (let ssrc of ssrcs) {
                if (ssrc.isMain) {
                    ssrcs = [ssrc];
                    break;
                }
            }
        }

        this.addHeader(conference.session_id, ssrcs);

        for (let entry of ssrcs) {
            this.addSsrcEntry(entry, conference.transport, isAnswer);
        }
    }

    static fromConference(conference: Conference, isAnswer = false) {
        const sdp = new SdpBuilder();
        sdp.addConference(conference, isAnswer);
        return sdp.finalize();
    }

    private toAudioSsrc(ssrc: Ssrc) {
        if (ssrc.isMain) {
            return '0';
        }

        return `audio${ssrc.ssrc}`;
    }
}
