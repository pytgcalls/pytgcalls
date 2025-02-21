# Whisper Example

## What is it?
This is an example on how to integrate STT (speech-to-text) with py-tgcalls via [OpenAI Whisper](https://openai.com/index/whisper/)

## How to use it?
Just follow these steps

1. Install **faster-whisper**
``` bash
pip3 install faster-whisper
```
2. Edit the config to best suit your needs (for example a faster or more accurate model)
3. Run the example
``` bash
python3 example_transcription.py
```
4. Let the called user talk, the example will wait for 2 seconds of silence before transcribing what the used said

## Hardware acceleration (NVIDIA GPU only)

The transcription process will run on GPU after installing [PyTorch](https://pytorch.org/get-started/locally/) (with CUDA support) and [CUDA](https://developer.nvidia.com/cuda-downloads)
