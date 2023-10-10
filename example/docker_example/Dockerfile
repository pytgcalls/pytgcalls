FROM amd64/python:3.9-buster
RUN python3.9 -m pip install py-tgcalls
RUN python3.9 -m pip install ntgcalls
RUN apt update && apt install -y ffmpeg
WORKDIR /usr/src/installer
COPY linux_mount.sh /usr/src/installer
RUN chmod +x /usr/src/installer/linux_mount.sh
VOLUME ['/usr/src/installer']
