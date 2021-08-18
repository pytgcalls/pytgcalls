FROM arm64v8/node:latest AS builder
WORKDIR /usr/src/pytgcalls
WORKDIR src
COPY src/* .
WORKDIR ..
COPY .npmignore .
COPY package.json .
COPY tsconfig.json .
RUN npm install
WORKDIR /usr/src/plaforms
COPY platforms/arm64v8/install_platform.sh /usr/src/plaforms
RUN chmod +x /usr/src/plaforms/install_platform.sh
VOLUME ['/usr/src/plaforms', '/usr/src/pytgcalls']