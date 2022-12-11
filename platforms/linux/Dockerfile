ARG python_version="3.6"
ARG dname="amd64"
ARG pname="manylinux2014_x86_64"
FROM ${dname}/python:${python_version}-buster
RUN \
  curl -fsSL https://deb.nodesource.com/setup_current.x | bash - &&\
  apt-get update && \
  apt-get install -y nodejs
WORKDIR /usr/src/pytgcalls
WORKDIR pytgcalls/
COPY pytgcalls/ .
WORKDIR ../src/
COPY src/* .
WORKDIR ..
COPY .npmignore .
COPY package.json .
COPY tsconfig.json .
COPY setup.py .
COPY LICENSE .
COPY README.md .
COPY requirements.txt .
ARG pname
ARG python_version
RUN python${python_version} setup.py sdist bdist_wheel --plat-name ${pname}
WORKDIR /usr/src/installer
COPY platforms/linux/linux_mount.sh /usr/src/installer
RUN chmod +x /usr/src/installer/linux_mount.sh
VOLUME ['/usr/src/installer', '/usr/src/pytgcalls']
