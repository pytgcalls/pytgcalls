import subprocess

from setuptools import setup
from setuptools.command.install import install


class PostInstall(install):
    def run(self):
        install.run(self)
        subprocess.call('install.sh')


setup(
    cmdclass={
        'install': PostInstall,
    },
)
