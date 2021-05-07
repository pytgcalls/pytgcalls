import os
import site

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
        node_result = self.get_version('node')
        npm_result = self.get_version('npm')
        if node_result['version_int'] == 0:
            raise Exception('This package requires Node.js to be installed')
        if npm_result['version_int'] == 0:
            raise Exception('This package requires npm to be installed')
        if node_result['version_int'] < 15:
            raise Exception(
                'This package requires Node.js 15 or newer, '
                f'current installed version is {node_result["version"]}',
            )
        if npm_result['version_int'] < 7:
            raise Exception(
                'This package requires npm 7 or newer, '
                f"current installed version is {npm_result['version']}",
            )
        os.system('npm install')
        if 'pip' in os.getcwd():
            if not os.path.exists(
                f'{site.getsitepackages()[0]}/pytgcalls',
            ):
                os.system(
                    'mkdir '
                    f'{site.getsitepackages()[0]}/pytgcalls',
                )
        os.system(
            'cp -r node_modules/ '
            f'{site.getsitepackages()[0]}/pytgcalls/node_modules',
        )
        install.run(self)


setup(
    cmdclass={
        'install': PostInstall,
    },
)
