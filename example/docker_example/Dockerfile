FROM python:3.13-slim
RUN apt update && apt install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
RUN python3.13 -m pip install py-tgcalls pyrogrammod tgcrypto -v