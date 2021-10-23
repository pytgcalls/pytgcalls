from os import system as cmd
from sys import executable

cmd('echo "deb https://deb.nodesource.com/node_16.x buster main" > /etc/apt/sources.list.d/nodesource.list')
cmd('wget -qO- https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add -')
cmd('echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list')
cmd('wget -qO- https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -')
cmd('apt-get update && apt-get install -yqq nodejs yarn')
cmd(f'{executable} -m pip install -U pip && {executable} -m pip install pipenv')
cmd('npm i -g npm@^7')
cmd(f'curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | {executable} && ln -s /root/.poetry/bin/poetry /usr/local/bin')
cmd('rm -rf /var/lib/apt/lists/*')
