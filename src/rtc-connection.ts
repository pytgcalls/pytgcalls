import fetch from "node-fetch";
import { TGCalls, Stream } from "./tgcalls";

class RTCConnection {
    chatId: number;
    filePath: string;
    port: number;
    bitrate: number;
    logMode: number;
    bufferLength: number;
    inviteHash: string;

    tgcalls: TGCalls<any>;
    stream: Stream;

    constructor(
        chatId: number,
        filePath: string,
        port: number,
        bitrate: number,
        logMode: number,
        bufferLength: number,
        inviteHash: string
    ) {
        this.chatId = chatId;
        this.filePath = filePath;
        this.port = port;
        this.bitrate = bitrate;
        this.logMode = logMode;
        this.bufferLength = bufferLength;
        this.inviteHash = inviteHash;

        this.tgcalls = new TGCalls({});
        this.stream = new Stream(
            filePath,
            16,
            bitrate,
            1,
            logMode,
            bufferLength
        );

        this.tgcalls.joinVoiceCall = async (payload: any) => {
            payload = {
                chatId: this.chatId,
                ufrag: payload.ufrag,
                pwd: payload.pwd,
                hash: payload.hash,
                setup: payload.setup,
                fingerprint: payload.fingerprint,
                source: payload.source,
                inviteHash: this.inviteHash,
            };

            if (logMode > 0) {
                console.log("callJoinPayload -> ", payload);
            }

            const joinCallResult = await (
                await fetch(`http://localhost:${this.port}/joinCall`, {
                    method: "POST",
                    body: JSON.stringify(payload),
                })
            ).json();

            if (logMode > 0) {
                console.log("joinCallRequestResult -> ", joinCallResult);
            }

            return joinCallResult;
        };

        this.stream.on("finish", async () => {
            await fetch(`http://localhost:${this.port}/streamEnded`, {
                method: "POST",
                body: JSON.stringify({
                    chatId: chatId,
                }),
            });
        });
    }

    async joinCall() {
        try {
            const result = await this.tgcalls.start(this.stream.createTrack());
            return result;
        } catch (e) {
            this.stream.stop();

            if (this.logMode > 0) {
                console.log("joinCallError ->", e);
            }

            return false;
        }
    }

    stop() {
        try {
            this.stream.stop();
            this.tgcalls.close();
        } catch (e) {}
    }

    async leaveCall() {
        try {
            this.stop();
            return await (
                await fetch(`http://localhost:${this.port}/leaveCall`, {
                    method: "POST",
                    body: JSON.stringify({
                        chatId: this.chatId,
                    }),
                })
            ).json();
        } catch (e) {
            return {
                action: "REQUEST_ERROR",
                message: e.toString(),
            };
        }
    }

    pause() {
        this.stream.pause();
    }

    async resume() {
        this.stream.resume();
    }

    setStream(filePath: string) {
        this.stream.setReadable(filePath);
    }
}

export default RTCConnection;
