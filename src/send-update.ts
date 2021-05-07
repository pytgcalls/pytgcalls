// @ts-ignore
import fetch from 'node-fetch';

export default async (port: number | string, params: any) => {
    await fetch(`http://localhost:${port}/update_request`, {
        method: 'POST',
        body: JSON.stringify(params),
    });
};
