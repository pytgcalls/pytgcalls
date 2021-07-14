// @ts-ignore
import fetch from 'node-fetch';
import { port } from './args';

export default (path: string, params: any) => {
    return fetch(`http://localhost:${port}/${path}`, {
        method: 'POST',
        body: JSON.stringify(params),
    });
};
