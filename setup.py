import os

from setuptools import setup

base_path = os.path.abspath(os.path.dirname(__file__))

about: dict = {}
with open(
    os.path.join(
        base_path,
        'pytgcalls',
        '__version__.py',
    ),
    encoding='utf-8',
) as f:
    exec(f.read(), about)

setup(
    version=about['__version__'],
    universal=True,
    zip_safe=False,
)
