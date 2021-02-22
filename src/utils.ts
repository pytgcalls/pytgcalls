import { Sdp } from './types';

export function parseSdp(sdp: string): Sdp {
    let lines = sdp.split('\r\n');

    let lookup = (prefix: string) => {
        for (let line of lines) {
            if (line.startsWith(prefix)) {
                return line.substr(prefix.length);
            }
        }

        return null;
    };

    let rawSource = lookup('a=ssrc:');
    return {
        fingerprint: lookup('a=fingerprint:')?.split(' ')[1] ?? null,
        hash: lookup('a=fingerprint:')?.split(' ')[0] ?? null,
        setup: lookup('a=setup:'),
        pwd: lookup('a=ice-pwd:'),
        ufrag: lookup('a=ice-ufrag:'),
        source: rawSource ? parseInt(rawSource.split(' ')[0]) : null,
    };
}
