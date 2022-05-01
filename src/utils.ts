import {Commands, CommandsInfo, Sdp} from './types';

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

    let rawAudioSource = lookup('a=ssrc:');
    let rawVideoSource = lookup('a=ssrc-group:FID ');
    return {
        fingerprint: lookup('a=fingerprint:')?.split(' ')[1] ?? null,
        hash: lookup('a=fingerprint:')?.split(' ')[0] ?? null,
        setup: lookup('a=setup:'),
        pwd: lookup('a=ice-pwd:'),
        ufrag: lookup('a=ice-ufrag:'),
        audioSource: rawAudioSource ? parseInt(rawAudioSource.split(' ')[0]) : null,
        source_groups: rawVideoSource ? rawVideoSource.split(' ').map(obj => {
            return parseInt(obj);
        }) : null,
    };
}

export function getBuiltCommands(stringCommand: string): Commands {
    let audioCommands;
    let videoCommands;
    if (stringCommand.includes('--audio')) {
        audioCommands = getBuiltSingleCommands(stringCommand.split('--audio')[1].split('--video')[0]);
    } else if (!stringCommand.includes('--video')) {
        audioCommands = getBuiltSingleCommands(stringCommand);
    } else {
        audioCommands = {
            before: [],
            middle: [],
            after: []
        };
    }
    if (stringCommand.includes('--video')) {
        videoCommands = getBuiltSingleCommands(stringCommand.split('--video')[1].split('--audio')[0]);
    } else if (!stringCommand.includes('--audio')) {
        videoCommands = getBuiltSingleCommands(stringCommand);
    } else {
        videoCommands = {
            before: [],
            middle: [],
            after: []
        };
    }
    return {
        audio: audioCommands,
        video: videoCommands,
    }
}

export function getBuiltSingleCommands(stringCommand: string): CommandsInfo {
    let beforeCmd = stringCommand.split('-atmid')[0].split('-atend')[0];
    let middleCmd = '';
    let afterCmd = '';
    if (stringCommand.includes('-atmid')) {
        middleCmd = stringCommand.split('-atmid')[1].split('-atend')[0];
    }
    if (stringCommand.includes('-atend')) {
        afterCmd = stringCommand.split('-atend')[1].split('-atmid')[0];
    }
    let listBeforeCmd = beforeCmd.split(':_cmd_:').filter(e =>  e);
    let listMiddleCmd = middleCmd.split(':_cmd_:').filter(e =>  e);
    let listAfterCmd = afterCmd.split(':_cmd_:').filter(e =>  e);
    return {
        before: listBeforeCmd,
        middle: listMiddleCmd,
        after: listAfterCmd,
    };
}
