import atexit
import os
import re
import socket
import time
from typing import Callable
from typing import Dict
from typing import List

import pyrogram
import requests
from pyrogram import Client
from pyrogram.raw.types import ChannelForbidden
from pyrogram.raw.types import GroupCall
from pyrogram.raw.types import GroupCallDiscarded
from pyrogram.raw.types import InputGroupCall
from pyrogram.raw.types import MessageActionInviteToGroupCall
from pyrogram.raw.types import UpdateChannel
from pyrogram.raw.types import UpdateGroupCall
from pyrogram.raw.types import UpdateNewChannelMessage

from . import __version__
from .methods import Methods
from .methods.core import env
from pytgcalls.methods.core import BColors


class PyTgCalls(Methods):
    def __init__(
            self,
            app: Client,
            port: int = 24859,
            log_mode: int = 0,
            flood_wait_cache: int = 120,
    ):
        self._app = app
        self._app_core = None
        self._sio = None
        self._host = 'localhost'
        self._port = port
        self._init_js_core = False
        self._on_event_update: Dict[str, list] = {
            'EVENT_UPDATE_HANDLER': [],
            'STREAM_END_HANDLER': [],
            'GROUP_CALL_HANDLER': [],
            'KICK_HANDLER': [],
            'CLOSED_HANDLER': [],
        }
        self._list_requests = [
            'request_join_call',
            'request_leave_call',
            'get_participants',
            'ended_stream',
            'update_request',
            'api_internal',
            'request_change_volume',
            'async_request',
            'api',
        ]
        self._waiting_start_request: List = []
        self._my_id = 0
        self.is_running = False
        self._calls: List[int] = []
        self._active_calls: Dict[int, str] = {}
        self._async_processes: Dict[str, Dict] = {}
        self._session_id = self._generate_session_id(20)
        self._log_mode = log_mode
        self._cache_user_peer: Dict[int, Dict] = {}
        self._cache_full_chat: Dict[int, Dict] = {}
        self._cache_local_peer = None
        self._flood_wait_cache = flood_wait_cache
        self.is_connected = False
        env.client_instances.append(self)
        atexit.register(self._before_close)
        super().__init__(self)

    @staticmethod
    def _get_version(package_check):
        result_cmd = os.popen(f'{package_check} -v').read()
        result_cmd = result_cmd.replace('v', '')
        if len(result_cmd) == 0:
            return None
        return result_cmd

    def run(self, before_start_callable: Callable = None):
        if self._app is not None:
            node_result = self._get_version('node')
            if node_result is None:
                raise Exception('Please install node (15.+)')
            if self._version_tuple(node_result) < \
                    self._version_tuple('15.0.0'):
                raise Exception(
                    'Needed node 15.+, '
                    'actually installed is '
                    f'{node_result}',
                )
            if self._version_tuple(pyrogram.__version__) < \
                    self._version_tuple('1.2.0'):
                raise Exception(
                    'Needed pyrogram 1.2.0+, '
                    'actually installed is '
                    f'{pyrogram.__version__}',
                )
            try:
                # noinspection PyBroadException
                @self._app.on_raw_update()
                async def on_close(client, update, _, data2):
                    if isinstance(update, UpdateGroupCall):
                        if isinstance(update.call, GroupCallDiscarded):
                            chat_id = int(f'-100{update.chat_id}')
                            self._cache_full_chat[chat_id] = {
                                'last_update': int(time.time()),
                                'full_chat': None,
                            }
                        if isinstance(update.call, GroupCall):
                            input_group_call = InputGroupCall(
                                access_hash=update.call.access_hash,
                                id=update.call.id,
                            )
                            chat_id = int(f'-100{update.chat_id}')
                            self._cache_full_chat[chat_id] = {
                                'last_update': int(time.time()),
                                'full_chat': input_group_call,
                            }
                    if isinstance(update, UpdateChannel):
                        chat_id = int(f'-100{update.channel_id}')
                        if len(data2) > 0:
                            if isinstance(
                                    data2[update.channel_id],
                                    ChannelForbidden,
                            ):
                                for event in self._on_event_update[
                                    'KICK_HANDLER'
                                ]:
                                    await event['callable'](
                                        chat_id,
                                    )
                                # noinspection PyBroadException
                                try:
                                    self.leave_group_call(
                                        chat_id,
                                        'kicked_from_group',
                                    )
                                except Exception:
                                    pass
                                try:
                                    del self._cache_user_peer[chat_id]
                                except Exception:
                                    pass
                    if isinstance(
                            update,
                            UpdateGroupCall,
                    ):
                        if isinstance(
                                update.call,
                                GroupCallDiscarded,
                        ):
                            chat_id = int(f'-100{update.chat_id}')
                            for event in self._on_event_update[
                                'CLOSED_HANDLER'
                            ]:
                                await event['callable'](
                                    chat_id,
                                )
                            # noinspection PyBroadException
                            try:
                                self.leave_group_call(
                                    chat_id,
                                    'closed_voice_chat',
                                )
                            except Exception:
                                pass
                            try:
                                del self._cache_user_peer[chat_id]
                            except Exception:
                                pass
                    if isinstance(
                            update,
                            UpdateNewChannelMessage,
                    ):
                        try:
                            if isinstance(
                                    update.message.action,
                                    MessageActionInviteToGroupCall,
                            ):
                                for event in self._on_event_update[
                                    'GROUP_CALL_HANDLER'
                                ]:
                                    await event['callable'](
                                        client, update.message,
                                    )
                        except Exception:
                            pass

                self._app.start()
                self._my_id = self._app.get_me()['id']  # noqa
                self._cache_local_peer = self._app.resolve_peer(
                    self._my_id,
                )
                if before_start_callable is not None:
                    # noinspection PyBroadException
                    try:
                        result = before_start_callable(self._my_id)
                        if isinstance(result, bool):
                            if not result:
                                return
                    except Exception:
                        pass
            except KeyboardInterrupt:
                pass
            self.is_connected = True
        else:
            raise Exception('NEED_PYROGRAM_CLIENT')
        return self

    # noinspection PyProtectedMember
    def _before_close(self):
        if not hasattr(env, 'running_server'):
            my_pos = -1
            list_instance = [
                instance for instance in env.client_instances
                if instance.is_connected and instance._app.is_connected
            ]
            warnings_mess = 0
            for i, instance in enumerate(list_instance):
                if instance is self:
                    my_pos = i + 1
                else:
                    port_test = instance._port
                    if port_test != 24859:
                        warnings_mess += 1
                        print(
                            BColors._WARNING +
                            f'WARNING: Unused port {port_test} '
                            f'at id {instance._my_id}!' +
                            BColors._ENDC,
                        )
                    instance.is_running = True
            if warnings_mess > 0:
                print('')  # FIX LINE SPACE
            if my_pos == len(list_instance):
                for instance in list_instance:
                    if instance is not self:
                        instance._port = self._port
                self._run_server()

    @staticmethod
    def _check_already_using(port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        is_in_use = s.connect_ex(('localhost', port)) == 0
        s.close()
        return is_in_use

    @staticmethod
    def _remote_version(branch: str):
        return re.findall(
            '__version__ = \'(.*?)\'', requests.get(
                f'https://raw.githubusercontent.com/'
                f'pytgcalls/pytgcalls/{branch}'
                f'/pytgcalls/__version__.py',
            ).text,
        )[0]

    @staticmethod
    def _version_tuple(v):
        list_version = []
        for vmj in v.split('.'):
            list_d = re.findall('[0-9]+', vmj)
            for vmn in list_d:
                list_version.append(int(vmn))
        return tuple(list_version)

    def _run_server(self):
        env.running_server = True
        print(
            f'PyTgCalls v{__version__}, Copyright (C) '
            f'2021 Laky-64 <https://github.com/Laky-64>\n'
            'Licensed under the terms of the GNU Lesser '
            'General Public License v3 or later (LGPLv3+)\n',
        )
        remote_stable_ver = self._remote_version('master')
        remote_dev_ver = self._remote_version('dev')
        if self._version_tuple(__version__) > \
                self._version_tuple(remote_stable_ver + '.99'):
            remote_ver = remote_readable_ver = remote_dev_ver
        else:
            remote_readable_ver = remote_stable_ver
            remote_ver = remote_stable_ver + '.99'
        if self._version_tuple(remote_ver) > self._version_tuple(__version__):
            print(
                BColors._WARNING + f'Update Available!\n'
                f'New PyTgCalls v{remote_readable_ver} is now available!\n' +
                BColors._ENDC,
            )
        if not self._check_already_using(self._port):
            self._spawn_process(
                self._run_js,
                (
                    f'{__file__.replace("pytgcalls.py", "")}dist/index.js',
                    f'port={self._port} log_mode={self._log_mode}',
                ),
            )
            self.is_running = True
            self._start_web_app()
        else:
            print(
                BColors._FAIL +
                f'Error: Port {self._port} already in use!' + BColors._ENDC,
            )

    def _add_handler(self, type_event: str, func):
        self._on_event_update[type_event].append(func)
