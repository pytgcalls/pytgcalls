import os

from setuptools import setup
from setuptools import Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install

from setup_helper import SetupHelper


class NodeJsExtension(Extension):
    def __init__(self, name, source_dir=''):
        Extension.__init__(self, name, sources=[])
        self.source_dir = os.path.abspath(source_dir)
        if not self.source_dir.endswith(os.path.sep):
            self.source_dir += os.path.sep


class PostInstall(install):
    def run(self):
        install.run(self)


class DockerBuild(build_ext):
    def run(self):
        build_ext.run(self)

    def build_extension(self, ext):
        ext_dir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
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
        'install': PostInstall,
    },
    zip_safe=False,
)
