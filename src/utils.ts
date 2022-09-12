import {Commands, CommandsInfo, Sdp} from './types';
import {webcrypto} from 'crypto';

export const second = <T>(_: any, s: T) => s;

export const uuid = (t=21) => webcrypto.getRandomValues(new Uint8Array(t)).reduce(((t,e)=>t+=(e&=63)<36?e.toString(36):e<62?(e-26).toString(36).toUpperCase():e>62?"-":"_"),"");

export function parseSdp(sdp: string): Sdp {
    let lines = sdp.split('\r\n');

    let lookup = (prefix: string) => {
        for (let line of lines) {
            if (line.startsWith(prefix)) {
                return line.substring(prefix.length);
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
    const beforeCmd = stringCommand.split('-atmid')[0].split('-atend')[0];
    let middleCmd = '';
    let afterCmd = '';
    if (stringCommand.includes('-atmid')) {
        middleCmd = stringCommand.split('-atmid')[1].split('-atend')[0];
    }
    if (stringCommand.includes('-atend')) {
        afterCmd = stringCommand.split('-atend')[1].split('-atmid')[0];
    }
    return {
        before: beforeCmd.split(':_cmd_:').filter(e =>  e),
        middle: middleCmd.split(':_cmd_:').filter(e =>  e),
        after: afterCmd.split(':_cmd_:').filter(e =>  e),
    };
}

export function getErrorMessage(error: string): string {
    if (error.includes('APP_UPGRADE_NEEDED')) {
        return 'APP_UPGRADE_NEEDED';
    } else if (error.includes('No transport') || error.includes('UNMUTE_NEEDED')) {
        return 'UNMUTE_NEEDED';
    }
    return 'JOIN_ERROR';
}

export enum LogLevel {
    DEBUG = 1,
    INFO,
    WARNING,
    ERROR,
}
