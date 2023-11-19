import os
from typing import Dict

from setuptools import find_packages
from setuptools import setup

base_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(base_path, 'README.md'), encoding='utf-8') as f:
    readme = f.read()

about: Dict = {}
with open(
    os.path.join(
        base_path,
        'pytgcalls',
        '__version__.py',
    ), encoding='utf-8',
) as f:
    exec(f.read(), about)

setup(
    name='py-tgcalls',
    version=about['__version__'],
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
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'ntgcalls>=1.0.0dev20',
        'psutil',
        'screeninfo',
        'deprecation',
    ],
    python_requires='>=3.8',
    include_package_data=True,
    universal=True,
    zip_safe=False,
)
