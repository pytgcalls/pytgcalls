# PyTgCalls

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/pytgcalls/pytgcalls/master.svg)](https://results.pre-commit.ci/latest/github/pytgcalls/pytgcalls/master)

# How to install?

Here's how to install the PyTgCalls lib, the commands are given below:

``` bash
cd pytgcalls/ && \
npm install && \
npm run prepare && \
cd pytgcalls/js && \
npm install && \
cd ../../ && \
pip install -r requirements.txt
```

# Conversion command

``` bash
ffmpeg -i {INPUT_FILE} -f s16le -ac 1 -acodec pcm_s16le -ar {BITRATE} {OUTPUT_FILE}
```

## Credits

Big thanks to [@evgeny-nadymov] for allowing us to use their code from [telegram-react]

This library is based on [tgcallsjs] developed [@AndrewLaneX] and pyservercall by [@Laky-64]

[@evgeny-nadymov]: https://github.com/evgeny-nadymov/
[@AndrewLaneX]: https://github.com/AndrewLaneX/
[telegram-react]: https://github.com/evgeny-nadymov/telegram-react/
[tgcallsjs]: https://github.com/tgcallsjs/tgcalls
[pyservercall]: https://github.com/pytgcalls/pyservercall/
[@Laky-64]: https://github.com/Laky-64/
