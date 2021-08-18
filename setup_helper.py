import os
import platform
import subprocess
import sys

import asyncio
import time


class SetupHelper:
    def __init__(
        self,
        source_dir: str,
        ext_dir: str,
        tmp_dir: str,
    ):
        folder_package = ''
        for item in sys.path:
            if 'dist-packages' in item or 'site-packages' in item:
                folder_package = item
                break
        self._source_dir = source_dir
        self._ext_dir = ext_dir
        self._tmp_dir = tmp_dir
        if not self._tmp_dir.endswith(os.path.sep):
            self._tmp_dir += os.path.sep
        self._folder_package = folder_package

    def clean_old_installation(self):
        subprocess.check_output(
            'rm -rf '
            f'{self._folder_package}/pytgcalls/node_modules',
            shell=True,
        )
        subprocess.check_output(
            'rm -rf '
            f'{self._folder_package}/pytgcalls/dist',
            shell=True,
        )
        subprocess.check_output(
            f'rm -rf {self._tmp_dir}',
            shell=True,
        )

    @property
    def _local_arch(self):
        pf = platform.machine()
        if pf == 'x86_64':
            pf = 'amd64'
        elif pf == 'aarch64':
            pf = 'arm64v8'
        else:
            raise UnsupportedArchitecture()
        return pf

    @property
    def _requested_arch(self):
        if len(sys.argv) == 5:
            arch = sys.argv[4]
            if arch == 'manylinux2014_x86_64':
                return 'amd64'
            elif arch == 'manylinux2014_aarch64':
                return 'arm64'
            else:
                raise UnsupportedArchitecture()
        return self._local_arch

    def run_installation(self):
        # COPY NEEDED FILES
        subprocess.check_output(
            f'cp -r {self._source_dir}platforms/ '
            f'{self._tmp_dir}platforms/',
            shell=True,
        )
        subprocess.check_output(
            f'cp -r {self._source_dir}src/ '
            f'{self._tmp_dir}src/',
            shell=True,
        )
        subprocess.check_output(
            f'cp -r {self._source_dir}package.json '
            f'{self._tmp_dir}',
            shell=True,
        )
        subprocess.check_output(
            f'cp -r {self._source_dir}tsconfig.json '
            f'{self._tmp_dir}',
            shell=True,
        )
        subprocess.check_output(
            f'cp -r {self._source_dir}.npmignore '
            f'{self._tmp_dir}',
            shell=True,
        )
        subprocess.check_output(
            f'cp -r {self._source_dir}platform_builder.sh '
            f'{self._tmp_dir}',
            shell=True,
        )
        # START COMPILATION
        subprocess.check_call(
            'bash platform_builder.sh '
            f'{self._requested_arch}',
            shell=True,
            cwd=self._tmp_dir
        )
        subprocess.check_output(
            'cp -r '
            f'{self._tmp_dir}platforms/build '
            f'{self._ext_dir}pytgcalls/platforms',
            shell=True,
        )


class UnsupportedArchitecture(Exception):
    def __init__(self):
        super().__init__()
