import os
import sys

from setuptools import setup
from setuptools.command.install import install

from pytgcalls.environment import Environment


class PostInstall(install):
    @staticmethod
    def get_version(package_check):
        result_cmd = os.popen(f'{package_check} -v').read()
        result_cmd = result_cmd.replace('v', '')
        if len(result_cmd) == 0:
            return None
        return result_cmd

    # noinspection PyBroadException
    def run(self):
        Environment(
            '15.0.0',
            '1.2.0'
        ).check_environment()
        os.system('npm install')
        folder_package = ''
        for item in sys.path:
            if 'dist-packages' in item or 'site-packages' in item:
                folder_package = item
                break
        if 'pip' in os.getcwd():
            print(
                'Copying files from '
                f'{os.getcwd()}/pytgcalls/'
                ' to '
                f'{folder_package}/pytgcalls/',
            )
            if not os.path.exists(
                f'{folder_package}/pytgcalls',
            ):
                os.system(
                    'mkdir '
                    f'{folder_package}/pytgcalls',
                )
            if os.path.exists(
                    f'{folder_package}/pytgcalls/dist',
            ):
                os.system(
                    'rm -r '
                    f'{folder_package}'
                    '/pytgcalls/dist',
                )
            if os.path.exists(
                    f'{folder_package}'
                    '/pytgcalls/node_modules',
            ):
                os.system(
                    'rm -r '
                    f'{folder_package}'
                    '/pytgcalls/node_modules',
                )
            os.system(
                'cp -r node_modules/ '
                f'{folder_package}/pytgcalls/node_modules',
            )
            os.system(
                'cp -r pytgcalls/dist/ '
                f'{folder_package}/pytgcalls/dist',
            )
        elif 'bdist_wheel' in sys.argv[2]:
            if os.path.exists(
                'pytgcalls/node_modules/',
            ):
                os.system(
                    'rm -r pytgcalls/node_modules/',
                )
            os.system(
                'cp -r node_modules/ pytgcalls/node_modules/',
            )
        install.run(self)


setup(
    cmdclass={
        'install': PostInstall,
    },
)
