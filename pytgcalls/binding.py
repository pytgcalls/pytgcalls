import asyncio
import atexit
import json
import logging
import os
import signal
import subprocess
import sys
from asyncio import Future
from asyncio.log import logger
from json import JSONDecodeError
from time import time
from typing import Callable

from .exceptions import WaitPreviousPingRequest


class Binding:
    def __init__(self):
        self._js_process = None
        self._ssid = ''
        self._on_request = None
        self._on_connect = None
        self._last_ping = 0
        self._waiting_ping = None

        def cleanup():
            async def async_cleanup():
                try:
                    if self._js_process is not None:
                        if not sys.platform.startswith('win'):
                            self._js_process.send_signal(signal.SIGINT)
                            await asyncio.wait_for(
                                self._js_process.communicate(),
                                timeout=3,
                            )
                        else:
                            self._js_process.kill()
                            await self._js_process.communicate()
                except subprocess.TimeoutExpired:
                    logger.warning(
                        'Node.js did not terminate cleanly, '
                        'killing process...',
                    )
                    self._js_process.kill()
                    await self._js_process.communicate()
                except ProcessLookupError:
                    pass
                logger.info('Node.js stopped')
            asyncio.get_event_loop().run_until_complete(async_cleanup())

        atexit.register(cleanup)

    def on_update(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._on_request = func
            return func

        return decorator

    def on_connect(self):
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._on_connect = func
            return func

        return decorator

    def is_alive(self):
        return int(time()) - self._last_ping < 15

    @property
    async def ping(self) -> float:
        if self._waiting_ping is None:
            start_time = time()
            self._waiting_ping = asyncio.Event()
            await self._send({
                'ping_with_response': True,
            })
            await self._waiting_ping.wait()
            self._waiting_ping = None
            return (time() - start_time) * 1000.0
        else:
            raise WaitPreviousPingRequest()

    @property
    def _run_folder(self):
        return f'{__file__.replace("binding.py", "")}'

    async def connect(
        self,
        event: Future,
        user_id: int,
    ):
        if self._js_process is None:
            sep = os.path.sep
            self._js_process = await asyncio.create_subprocess_exec(
                'node',
                f'{self._run_folder}dist{sep}index.js',
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
            event.set_result(None)
            while True:
                try:
                    if self._js_process.stdout is None:
                        break
                    out = (await self._js_process.stdout.readline())\
                        .decode().replace('\n', '').replace('\r', '')
                    try:
                        json_out = json.loads(out)
                        if 'ping_with_response' and \
                                self._waiting_ping is not None:
                            self._waiting_ping.set()
                        if 'ping' in json_out:
                            self._last_ping = int(time())
                        if 'try_connect' in json_out:
                            self._ssid = json_out['try_connect']
                            asyncio.ensure_future(
                                self._send({
                                    'try_connect': 'connected',
                                    'user_id': user_id,
                                }),
                            )
                            asyncio.ensure_future(self._on_connect())
                        elif 'ssid' in json_out and 'uid' in json_out:
                            if json_out['ssid'] == self._ssid:
                                if self._on_request is not None:
                                    async def future_response(
                                        future_json_out: dict,
                                    ):
                                        result = await self._on_request(
                                            future_json_out['data'],
                                        )
                                        if isinstance(result, dict):
                                            await self._send_response(
                                                result,
                                                future_json_out['uid'],
                                            )
                                        else:
                                            await self._send_error(
                                                'INVALID_RESPONSE',
                                                future_json_out['uid'],
                                            )
                                    asyncio.ensure_future(
                                        future_response(json_out),
                                    )
                        elif 'log_message' in json_out \
                                and 'verbose_mode' in json_out:
                            if json_out['verbose_mode'] == 1:
                                logging.debug(json_out['log_message'])
                            elif json_out['verbose_mode'] == 2:
                                logging.info(json_out['log_message'])
                            elif json_out['verbose_mode'] == 3:
                                logging.warning(json_out['log_message'])
                            elif json_out['verbose_mode'] == 4:
                                logging.error(json_out['log_message'])
                    except JSONDecodeError:
                        if not out:
                            break
                        if ':replace_line:' in out:
                            print(out.replace(':replace_line:', ''), end='\r')
                        else:
                            print(out)
                except TimeoutError:
                    pass

    async def _send_response(self, json_data: dict, uid: str):
        if self._ssid:
            await self._send({
                'data': json_data,
                'uid': uid,
                'ssid': self._ssid,
            })

    async def _send_error(self, err_mess: str, uid: str):
        if self._ssid:
            await self._send({
                'err_mess': err_mess,
                'uid': uid,
                'ssid': self._ssid,
            })

    async def send(self, json_data: dict):
        await self._send({
            'data': json_data,
            'ssid': self._ssid,
        })

    async def _send(self, json_data: dict):
        try:
            self._js_process.stdin.write(json.dumps(json_data).encode())
            await self._js_process.stdin.drain()
        except ConnectionResetError:
            pass
