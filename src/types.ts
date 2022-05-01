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
    ssrc: number;
    ssrc_group: Array<number>,
}

export interface Sdp {
    fingerprint: string | null;
    hash: string | null;
    setup: string | null;
    pwd: string | null;
    ufrag: string | null;
    audioSource: number | null;
    source_groups: Array<number> | null;
}

export interface CommandsInfo {
    before: Array<string>;
    middle: Array<string>;
    after: Array<string>;
}

export interface Commands {
    audio: CommandsInfo;
    video: CommandsInfo;
}

export interface JoinVoiceCallParams<T> {
    ufrag: string;
    pwd: string;
    hash: string;
    setup: 'active';
    fingerprint: string;
    source: number;
    source_groups: Array<number>;
    params: T;
}

export interface JoinVoiceCallResponse {
    transport: Transport | null;
}

export type JoinVoiceCallCallback<T> = (
    payload: JoinVoiceCallParams<T>,
) => Promise<JoinVoiceCallResponse>;

export interface RemotePlayingTimeResponse {
    time?: number;
}

export type RemotePlayingTimeCallback = (
) => RemotePlayingTimeResponse;

export interface RemoteLaggingResponse {
    isLagging: boolean;
}

export type RemoteLaggingCallback = (
) => RemoteLaggingResponse;

export type onData = (
    data: any,
) => void;

export type onEnd = (
) => void;
