import os
import re
import sys

from setuptools import setup
from setuptools.command.install import install


class PostInstall(install):
    @staticmethod
    def get_version(package_check):
        result_cmd = os.popen(f'{package_check} -v').read()
        result_cmd = result_cmd.replace('v', '')
        if len(result_cmd) == 0:
            return None
        return result_cmd

    @staticmethod
    def _version_tuple(v):
        list_version = []
        for vmj in v.split('.'):
            list_d = re.findall('[0-9]+', vmj)
            for vmn in list_d:
                list_version.append(int(vmn))
        return tuple(list_version)

    # noinspection PyBroadException
    def run(self):
        if sys.platform.startswith('win'):
            raise Exception(
                'Installation from GitHub isn\'t supported on your platform.'
                '\nInstall with\n\npip3 install py-tgcalls -U',
            )
        node_result = self.get_version('node')
        npm_result = self.get_version('npm')
        if node_result is None:
            raise Exception('Please install node (15.+)')
        if npm_result is None:
            raise Exception('Please install npm (7.+)')
        if self._version_tuple(node_result) < self._version_tuple('15.0.0'):
            raise Exception(
                'Needed node 15.+, '
                'actually installed is '
                f'{node_result}',
            )
        if self._version_tuple(npm_result) < self._version_tuple('7.0.0'):
            raise Exception(
                'Needed npm 7.+, '
                'actually installed is '
                f'{npm_result}',
            )
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
