import os
import platform
import subprocess
import sys

from setuptools import Extension
from setuptools import setup
from setuptools.command.build_ext import build_ext


class NodeJsExtension(Extension):
    def __init__(self, name, source_dir=''):
        Extension.__init__(self, name, sources=[])
        self.source_dir = os.path.abspath(source_dir)
        if not self.source_dir.endswith(os.path.sep):
            self.source_dir += os.path.sep


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

    def run_installation(self):
        # COPY NEEDED FILES
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
        # START COMPILATION
        subprocess.check_call(
            'npm install .',
            shell=True,
            cwd=self._tmp_dir,
        )
        subprocess.check_output(
            'cp -r '
            f'{self._tmp_dir}node_modules '
            f'{self._ext_dir}pytgcalls/',
            shell=True,
        )
        subprocess.check_output(
            'cp -r '
            f'{self._tmp_dir}pytgcalls/dist '
            f'{self._ext_dir}pytgcalls/',
            shell=True,
        )


class UnsupportedArchitecture(Exception):
    def __init__(self):
        super().__init__()


class DockerBuild(build_ext):
    def run(self):
        build_ext.run(self)

    def build_extension(self, ext):
        ext_dir = os.path.abspath(
            os.path.dirname(self.get_ext_fullpath(ext.name)),
        )
        if not ext_dir.endswith(os.path.sep):
            ext_dir += os.path.sep
        sh = SetupHelper(
            ext.source_dir,
            ext_dir,
            self.build_temp,
        )
        sh.clean_old_installation()
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        sh.run_installation()


setup(
    ext_modules=[NodeJsExtension('pytgcalls')],
    cmdclass={
        'build_ext': DockerBuild,
    },
    zip_safe=False,
)
