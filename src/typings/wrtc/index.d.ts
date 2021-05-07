// https://github.com/node-webrtc/node-webrtc/pull/656
/// <reference lib="dom" />

declare module 'wrtc' {
    export const MediaStream: {
        prototype: MediaStream;
        new (): MediaStream;
        new (stream: MediaStream): MediaStream;
        new (tracks: MediaStreamTrack[]): MediaStream;
        new ({ id }: { id: string }): MediaStream;
    };

    export const MediaStreamTrack: {
        prototype: MediaStreamTrack;
        new (): MediaStreamTrack;
    };

    export const RTCDataChannel: {
        prototype: RTCDataChannel;
        new (): RTCDataChannel;
    };

    export const RTCDataChannelEvent: {
        prototype: RTCDataChannelEvent;
        new (
            type: string,
            eventInitDict: RTCDataChannelEventInit
        ): RTCDataChannelEvent;
    };

    export const RTCDtlsTransport: {
        prototype: RTCDtlsTransport;
        new (): RTCDtlsTransport;
    };

    export const RTCIceCandidate: {
        prototype: RTCIceCandidate;
        new (candidateInitDict?: RTCIceCandidateInit): RTCIceCandidate;
    };

    export const RTCIceTransport: {
        prototype: RTCIceTransport;
        new (): RTCIceTransport;
    };

    export type ExtendedRTCConfiguration = RTCConfiguration & {
        portRange?: {
            min: number;
            max: number;
        };
        sdpSemantics?: 'plan-b' | 'unified-plan';
    };

    export const RTCPeerConnection: {
        prototype: RTCPeerConnection;
        new (configuration?: ExtendedRTCConfiguration): RTCPeerConnection;
        generateCertificate(
            keygenAlgorithm: AlgorithmIdentifier
        ): Promise<RTCCertificate>;
        getDefaultIceServers(): RTCIceServer[];
    };

    export const RTCPeerConnectionIceEvent: {
        prototype: RTCPeerConnectionIceEvent;
        new (
            type: string,
            eventInitDict?: RTCPeerConnectionIceEventInit
        ): RTCPeerConnectionIceEvent;
    };

    export const RTCRtpReceiver: {
        prototype: RTCRtpReceiver;
        new (): RTCRtpReceiver;
        getCapabilities(kind: string): RTCRtpCapabilities | null;
    };

    export const RTCRtpSender: {
        prototype: RTCRtpSender;
        new (): RTCRtpSender;
        getCapabilities(kind: string): RTCRtpCapabilities | null;
    };

    export const RTCRtpTransceiver: {
        prototype: RTCRtpTransceiver;
        new (): RTCRtpTransceiver;
    };

    export const RTCSctpTransport: {
        prototype: RTCSctpTransport;
        new (): RTCSctpTransport;
    };

    export const RTCSessionDescription: {
        prototype: RTCSessionDescription;
        new (
            descriptionInitDict?: RTCSessionDescriptionInit
        ): RTCSessionDescription;
    };

    export const getUserMedia: (
        constraints?: MediaStreamConstraints
    ) => Promise<MediaStream>;

    export const mediaDevices: MediaDevices;

    export interface RTCAudioData {
        samples: Int16Array;
        sampleRate: number;
        bitsPerSample?: number;
        channelCount?: number;
        numberOfFrames?: number;
    }

    export interface RTCAudioDataEvent extends RTCAudioData, Event {
        type: 'data';
    }

    export interface RTCAudioSource {
        createTrack(): MediaStreamTrack;
        onData(data: RTCAudioData): void;
    }

    interface DataEventListener extends EventListener {
        (data: RTCAudioDataEvent): void;
    }

    interface DataEventListenerObject extends EventListenerObject {
        handleEvent(evt: RTCAudioDataEvent): void;
    }

    export interface RTCAudioSink extends EventTarget {
        stop(): void;
        readonly stopped: boolean;
        ondata: ((this: RTCAudioSink, ev: RTCAudioDataEvent) => any) | null;
        addEventListener(
            type: 'data',
            listener: DataEventListener | DataEventListenerObject | null,
            options?: boolean | AddEventListenerOptions
        ): void;
        removeEventListener(
            type: 'data',
            callback: DataEventListener | DataEventListenerObject | null,
            options?: EventListenerOptions | boolean
        ): void;
    }

    export interface RTCVideoFrame {
        width: number;
        height: number;
        data: Uint8ClampedArray;
        rotation?: number;
    }

    export interface RTCVideoFrameEvent extends Event {
        type: 'frame';
        frame: RTCVideoFrame;
    }

    interface FrameEventListener extends EventListener {
        (data: RTCVideoFrameEvent): void;
    }

    interface FrameEventListenerObject extends EventListenerObject {
        handleEvent(evt: RTCVideoFrameEvent): void;
    }

    export interface RTCVideoSourceInit {
        isScreencast?: boolean;
        needsDenoising?: boolean;
    }

    export interface RTCVideoSource {
        readonly isScreencast: boolean;
        readonly needsDenoising?: boolean;
        createTrack(): MediaStreamTrack;
        onFrame(frame: RTCVideoFrame): void;
    }

    export interface RTCVideoSink {
        stop(): void;
        readonly stopped: boolean;
        onframe: ((this: RTCVideoSink, ev: RTCVideoFrameEvent) => any) | null;
        addEventListener(
            type: 'data',
            listener: FrameEventListener | FrameEventListenerObject | null,
            options?: boolean | AddEventListenerOptions
        ): void;
        removeEventListener(
            type: 'data',
            callback: FrameEventListener | FrameEventListenerObject | null,
            options?: EventListenerOptions | boolean
        ): void;
    }

    export const nonstandard: {
        RTCAudioSource: {
            prototype: RTCAudioSource;
            new (): RTCAudioSource;
        };
        RTCAudioSink: {
            prototype: RTCAudioSink;
            new (track: MediaStreamTrack): RTCAudioSink;
        };
        RTCVideoSource: {
            prototype: RTCVideoSource;
            new (init?: RTCVideoSourceInit): RTCVideoSource;
        };
        RTCVideoSink: {
            prototype: RTCVideoSink;
            new (track: MediaStreamTrack): RTCVideoSink;
        };
        i420ToRgba(
            i420Frame: {
                width: number;
                height: number;
                data: Uint8ClampedArray;
            },
            rgbaFrame: {
                width: number;
                height: number;
                data: Uint8ClampedArray;
            }
        ): void;
        rgbaToI420(
            i420Frame: {
                width: number;
                height: number;
                data: Uint8ClampedArray;
            },
            rgbaFrame: {
                width: number;
                height: number;
                data: Uint8ClampedArray;
            }
        ): void;
    };
}
