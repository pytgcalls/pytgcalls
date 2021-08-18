FROM amd64/node:latest AS builder
RUN apt update
RUN apt install python3 -y
RUN apt install python3-pip -y
RUN pip3 install setuptools
WORKDIR /usr/src/pytgcalls
WORKDIR pytgcalls/
COPY pytgcalls/* .
WORKDIR ../src/
COPY src/* .
WORKDIR ..
COPY .npmignore .
COPY package.json .
COPY tsconfig.json .
COPY setup.py .
COPY setup.cfg .
COPY LICENSE .
COPY README.md .
COPY requirements.txt .
RUN python3 setup.py sdist bdist_wheel
WORKDIR /usr/src/installer
COPY platforms/amd64/install_platform.sh /usr/src/installer
RUN chmod +x /usr/src/installer/install_platform.sh
VOLUME ['/usr/src/installer', '/usr/src/pytgcalls']
