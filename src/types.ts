export interface Fingerprint {
    hash: string;
    fingerprint: string;
}

export interface Transport {
    ufrag: string;
    pwd: string;
    fingerprints: Fingerprint[];
    candidates: Candidate[];
}

export interface Conference {
    session_id: number;
    transport: Transport;
    ssrcs: Ssrc[];
}

export interface Candidate {
    generation: string;
    component: string;
    protocol: string;
    port: string;
    ip: string;
    foundation: string;
    id: string;
    priority: string;
    type: string;
    network: string;
}

export interface Ssrc {
    isMain: boolean;
    isRemoved?: boolean;
    ssrc: number;
}

export interface Sdp {
    fingerprint: string | null;
    hash: string | null;
    setup: string | null;
    pwd: string | null;
    ufrag: string | null;
    source: number | null;
}

export interface JoinVoiceCallParams<T> {
    ufrag: string;
    pwd: string;
    hash: string;
    setup: 'active';
    fingerprint: string;
    source: number;
    params: T;
}

export interface JoinVoiceCallResponse {
    transport: Transport | null;
}

export type JoinVoiceCallCallback<T> = (
    payload: JoinVoiceCallParams<T>
) => Promise<JoinVoiceCallResponse>;
