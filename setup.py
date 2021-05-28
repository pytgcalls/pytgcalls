import os
import sys

from setuptools import setup
from setuptools.command.install import install


class PostInstall(install):
    @staticmethod
    def get_version(package_check):
        result_cmd = os.popen(f'{package_check} -v').read()
        result_cmd = result_cmd.replace('v', '')
        if len(result_cmd) == 0:
            return {
                'version_int': 0,
                'version': '0',
            }
        return {
            'version_int': int(result_cmd.split('.')[0]),
            'version': result_cmd,
        }

    # noinspection PyBroadException
    def run(self):
        if sys.platform.startswith('win'):
            raise Exception(
                'Installation from GitHub isn\'t supported on your platform.'
                '\nInstall with\n\npip3 install py-tgcalls -U',
            )
        node_result = self.get_version('node')
        npm_result = self.get_version('npm')
        if node_result['version_int'] == 0:
            raise Exception('Please install node (15.+)')
        if npm_result['version_int'] == 0:
            raise Exception('Please install npm (7.+)')
        if node_result['version_int'] < 15:
            raise Exception(
                'Needed node 15.+, '
                'actually installed is '
                f"{node_result['version']}",
            )
        if npm_result['version_int'] < 7:
            raise Exception(
                'Needed npm 7.+, '
                'actually installed is '
                f"{npm_result['version']}",
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
