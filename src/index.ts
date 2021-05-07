import { connect } from "socket.io-client";
import RTCConnection from "./rtc-connection";
import sendUpdate from "./send-update";

(async () => {
    const port = parseInt(process.argv[2].split("=")[1]);
    const logMode = parseInt(process.argv[3].split("=")[1]);
    let socket = connect(`ws://localhost:${port}`);
    console.log(`Starting on port: ${port}`);
    socket.on("connect", () =>
        console.log("\x1b[32m", "Node.js core started!", "\x1b[0m")
    );

    let connections: Array<RTCConnection> = [];

    await socket.on("request", async function (data: any) {
        data = JSON.parse(data);

        if (logMode > 0) {
            console.log("REQUEST: ", data);
        }

        if (data["action"] === "joinCall") {
            if (!connections[data.chatId]) {
                connections[data.chatId] = new RTCConnection(
                    data.chatId,
                    data["filePath"],
                    port,
                    data["bitrate"],
                    logMode,
                    data["bufferLength"],
                    data["inviteHash"]
                );

                const result = await connections[data.chatId].joinCall();

                if (result) {
                    await sendUpdate(port, {
                        result: "JOINED_VOICE_CHAT",
                        chatId: data.chatId,
                    });
                } else {
                    delete connections[data.chatId];
                    await sendUpdate(port, {
                        result: "JOIN_ERROR",
                        chatId: data.chatId,
                    });
                }

                if (logMode > 0) {
                    console.log("UPDATED_CONNECTIONS: ", connections);
                }
            }
        } else if (data["action"] === "leaveCall") {
            if (connections[data.chatId]) {
                if (data["type"] !== "kicked_from_group") {
                    let result = await connections[data.chatId].leaveCall();

                    if (result["result"] === "OK") {
                        delete connections[data.chatId];
                        await sendUpdate(port, {
                            result: "LEFT_VOICE_CHAT",
                            chatId: data.chatId,
                        });
                    } else {
                        if (logMode > 0) {
                            console.log("ERROR_INTERNAL: ", result);
                        }

                        delete connections[data.chatId];
                        await sendUpdate(port, {
                            result: "LEFT_VOICE_CHAT",
                            error: result["result"],
                            chatId: data.chatId,
                        });
                    }
                } else {
                    await connections[data.chatId].stop();
                    delete connections[data.chatId];
                    await sendUpdate(port, {
                        result: "KICKED_FROM_GROUP",
                        chatId: data.chatId,
                    });
                }
            }
        } else if (data["action"] === "pause") {
            if (connections[data.chatId]) {
                try {
                    await connections[data.chatId].pause();
                    await sendUpdate(port, {
                        result: "PAUSED_AUDIO_STREAM",
                        chatId: data.chatId,
                    });
                } catch (e) {}
            }
        } else if (data["action"] === "resume") {
            if (connections[data.chatId]) {
                try {
                    await connections[data.chatId].resume();
                    await sendUpdate(port, {
                        result: "RESUMED_AUDIO_STREAM",
                        chatId: data.chatId,
                    });
                } catch (e) {}
            }
        } else if (data["action"] === "changeStream") {
            if (connections[data.chatId]) {
                try {
                    await connections[data.chatId].changeStream(data.filePath);
                    await sendUpdate(port, {
                        result: "CHANGED_AUDIO_STREAM",
                        chatId: data.chatId,
                    });
                } catch (e) {}
            }
        }
    });
})();
