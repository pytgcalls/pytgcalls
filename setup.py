import os

from setuptools import find_packages
from setuptools import setup

base_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(base_path, 'README.md'), encoding='utf-8') as f:
    readme = f.read()

setup(
    name='py-tgcalls',
    version='1.0.0.dev1',
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
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'ntgcalls',
        'psutil',
        'screeninfo',
        'deprecation',
    ],
    python_requires='>=3.7',
    include_package_data=True,
    universal=True,
    zip_safe=False,
)
