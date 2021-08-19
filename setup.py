import os
import shutil
import subprocess
import sys

from setuptools import Extension
from setuptools import find_packages
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
        # CHECK IF IS INSTALLATION FROM PYPI
        sep = os.path.sep
        if os.path.isdir(f'{self._source_dir}src{sep}'):
            try:
                shutil.rmtree(
                    f'{self._folder_package}{sep}pytgcalls{sep}node_modules',
                )
            except OSError:
                pass
            try:
                shutil.rmtree(f'{self._folder_package}{sep}pytgcalls{sep}dist')
            except OSError:
                pass
            try:
                shutil.rmtree(f'{self._tmp_dir}')
            except OSError:
                pass

    def run_installation(self):
        # CHECK IF IS INSTALLATION FROM PYPI
        sep = os.path.sep
        if os.path.isdir(f'{self._source_dir}src{sep}'):
            # COPY NEEDED FILES
            shutil.copytree(
                f'{self._source_dir}src{sep}',
                f'{self._tmp_dir}src{sep}',
            )
            shutil.copyfile(
                f'{self._source_dir}package.json',
                f'{self._tmp_dir}package.json',
            )
            shutil.copyfile(
                f'{self._source_dir}tsconfig.json',
                f'{self._tmp_dir}tsconfig.json',
            )
            shutil.copyfile(
                f'{self._source_dir}.npmignore',
                f'{self._tmp_dir}.npmignore',
            )
            # START COMPILATION
            subprocess.check_call(
                'npm install .',
                shell=True,
                cwd=self._tmp_dir,
            )
            shutil.copytree(
                f'{self._tmp_dir}node_modules{sep}',
                f'{self._ext_dir}pytgcalls{sep}node_modules{sep}',
            )
            shutil.copytree(
                f'{self._tmp_dir}dist{sep}',
                f'{self._ext_dir}pytgcalls{sep}dist{sep}',
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
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        sh = SetupHelper(
            ext.source_dir,
            ext_dir,
            self.build_temp,
        )
        sh.clean_old_installation()
        sh.run_installation()


setup(
    name='py_tgcalls',
    version='0.7.0.rc11',
    long_description='file: README.md',
    long_description_content_type='text/markdown',
    url='https://github.com/pytgcalls/pytgcalls',
    author='Laky-64',
    author_email='iraci.matteo@gmail.com',
    license='LGPL-3.0',
    license_file='LICENSE',
    classifiers=[
        'License :: OSI Approved :: '
        'GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    ext_modules=[NodeJsExtension('pytgcalls')],
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'httpx',
        'psutil',
        'pyrogram',
        'tgcrypto',
    ],
    python_requires='>=3.6.1',
    include_package_data=True,
    universal=True,
    cmdclass={
        'build_ext': DockerBuild,
    },
    zip_safe=False,
)
