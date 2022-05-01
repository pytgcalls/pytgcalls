import asyncio
import re
import subprocess
from sys import platform

from screeninfo import get_monitors
from screeninfo import ScreenInfoError

from ..types.list import List
from .device_info import DeviceInfo
from .screen_info import ScreenInfo


class MediaDevices:
    @staticmethod
    async def get_screen_devices() -> List:
        list_screens: List = List()
        if platform != 'darwin':
            try:
                for screen in get_monitors():
                    list_screens.append(
                        ScreenInfo(
                            screen.x,
                            screen.y,
                            screen.width,
                            screen.height,
                            screen.is_primary,
                            screen.name,
                        ),
                    )
            except ScreenInfoError:
                pass
        return list_screens

    @staticmethod
    async def get_audio_devices() -> List:
        list_devices: List = List()
        if platform == 'darwin':
            return list_devices
        try:
            if platform == 'win32':
                commands = [
                    'ffmpeg',
                    '-list_devices',
                    'true',
                    '-f',
                    'dshow',
                    '-i',
                    'dummy',
                ]
            else:
                commands = [
                    'pactl',
                    'list',
                    'sources',
                ]
            ffmpeg = await asyncio.create_subprocess_exec(
                *tuple(commands),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    ffmpeg.communicate(),
                    timeout=3,
                )
                result: str = ''
                if platform == 'win32':
                    result = stderr.decode('utf-8')
                elif platform != 'darwin':
                    result = stdout.decode('utf-8')
            except subprocess.TimeoutExpired:
                return list_devices
            if platform == 'win32':
                list_raw = result.split('DirectShow audio devices')[1]
                output = re.findall(
                    '\\[.*?].*?"(.*?)".*?\n\\[.*?].*?"(.*?)"', list_raw,
                )
                for device in output:
                    list_devices.append(
                        DeviceInfo(
                            device[1],
                            device[0],
                        ),
                    )
            else:
                output = re.findall(
                    'Name: (.*?)\n.*?Description: (.*?)\n', result,
                )
                for device in output:
                    list_devices.append(
                        DeviceInfo(
                            device[0],
                            device[1],
                        ),
                    )
        except FileNotFoundError:
            pass
        return list_devices
