import subprocess

from setuptools import setup
from setuptools.command.install import install


class PostInstall(install):
    def run(self):
        install.run(self)
        subprocess.run(['npm', 'install'], cwd='pytgcalls/js')


setup(
    cmdclass={
        'install': PostInstall,
    },
)
