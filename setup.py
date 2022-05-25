import os
import shutil
import subprocess
import sys

from setuptools import Extension
from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_ext import build_ext

base_path = os.path.abspath(os.path.dirname(__file__))


class NodeJsExtension(Extension):
    def __init__(self, name, source_dir=''):
        super().__init__(name, sources=[])
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


class NodeJsBuilder(build_ext):
    def run(self):
        super().run()

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


with open(os.path.join(base_path, 'README.md'), encoding='utf-8') as f:
    readme = f.read()

setup(
    name='py-tgcalls',
    version='0.9.1',
    long_description=readme,
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    ext_modules=[NodeJsExtension('pytgcalls')],
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'psutil',
        'screeninfo',
    ],
    python_requires='>=3.6.1',
    include_package_data=True,
    universal=True,
    cmdclass={
        'build_ext': NodeJsBuilder,
    },
    zip_safe=False,
)
