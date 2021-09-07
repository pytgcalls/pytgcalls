import { Candidate, Conference, Transport } from './types';

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
            `${c.foundation} ${c.component} ${c.protocol} ${c.priority} ${c.ip} ${c.port} typ ${c.type}`,
        );
        this.push(` generation ${c.generation}`);
        this.addJoined();
    }

    addHeader(session_id: number) {
        this.add('v=0');
        this.add(`o=- ${session_id} 2 IN IP4 0.0.0.0`);
        this.add('s=-');
        this.add('t=0 0');
        this.add(`a=group:BUNDLE 0 1`);
        this.add('a=ice-lite');
    }

    addTransport(transport: Transport) {
        this.add(`a=ice-ufrag:${transport.ufrag}`);
        this.add(`a=ice-pwd:${transport.pwd}`);

        for (let fingerprint of transport.fingerprints) {
            this.add(
                `a=fingerprint:${fingerprint.hash} ${fingerprint.fingerprint}`,
            );
            this.add(`a=setup:passive`);
        }

        let candidates = transport.candidates;
        for (let candidate of candidates) {
            this.addCandidate(candidate);
        }
    }

    addSsrcEntry(transport: Transport) {
        //AUDIO CODECS
        this.add(`m=audio 1 RTP/SAVPF 111 126`);
        this.add('c=IN IP4 0.0.0.0');
        this.add(`a=mid:0`);
        this.addTransport(transport);
        this.add('a=rtpmap:111 opus/48000/2');
        this.add('a=rtpmap:126 telephone-event/8000');
        this.add('a=fmtp:111 minptime=10; useinbandfec=1; usedtx=1');
        this.add('a=rtcp:1 IN IP4 0.0.0.0');
        this.add('a=rtcp-mux');
        this.add('a=rtcp-fb:111 transport-cc');
        this.add('a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level');
        this.add('a=recvonly');
        //END AUDIO CODECS

        //VIDEO CODECS
        this.add(`m=video 1 RTP/SAVPF 100 101 102 103`);
        this.add('c=IN IP4 0.0.0.0');
        this.add(`a=mid:1`);
        this.addTransport(transport);

        //VP8 CODEC
        this.add('a=rtpmap:100 VP8/90000/1');
        this.add('a=fmtp:100 x-google-start-bitrate=800');
        this.add('a=rtcp-fb:100 goog-remb');
        this.add('a=rtcp-fb:100 transport-cc');
        this.add('a=rtcp-fb:100 ccm fir');
        this.add('a=rtcp-fb:100 nack');
        this.add('a=rtcp-fb:100 nack pli');
        this.add('a=rtpmap:101 rtx/90000');
        this.add('a=fmtp:101 apt=100');

        //VP9 CODEC
        this.add('a=rtpmap:102 VP9/90000/1');
        this.add('a=rtcp-fb:102 goog-remb');
        this.add('a=rtcp-fb:102 transport-cc');
        this.add('a=rtcp-fb:102 ccm fir');
        this.add('a=rtcp-fb:102 nack');
        this.add('a=rtcp-fb:102 nack pli');
        this.add('a=rtpmap:103 rtx/90000');
        this.add('a=fmtp:103 apt=102');

        this.add('a=recvonly');
        this.add('a=rtcp:1 IN IP4 0.0.0.0');
        this.add('a=rtcp-mux');
        //END VIDEO CODECS
    }

    addConference(conference: Conference) {
        this.addHeader(conference.session_id);
        this.addSsrcEntry(conference.transport);
    }

    static fromConference(conference: Conference) {
        const sdp = new SdpBuilder();
        sdp.addConference(conference);
        return sdp.finalize();
    }
}
