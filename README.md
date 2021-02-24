# PyTgCalls

# Installation
You can install the lib, running the following commands:

``` bash
cd pytgcalls/ && \
npm install && \
npm run prepare && \
cd pytgcalls/ && \
npm install && \
cd ../ && \
pip install -r requirements.txt
```

# Convertion command
``` bash
ffmpeg -i {INPUT_FILE} -f s16le -ac 1 -acodec pcm_s16le -ar {BITRATE} {OUTPUT_FILE}
```

## Credits

Big thanks to [@evgeny-nadymov] for allowing us to use their code from [telegram-react].

This library is based on [tgcallsjs] and [pyservercall] and developed by [@AndrewLaneX] and [@Laky-64].

[@evgeny-nadymov]: https://github.com/evgeny-nadymov/
[@AndrewLaneX]: https://github.com/AndrewLaneX/
[telegram-react]: https://github.com/evgeny-nadymov/telegram-react/
[tgcallsjs]: https://github.com/tgcallsjs/tgcalls
[pyservercall]: https://github.com/pytgcalls/pyservercall/
[@Laky-64]: https://github.com/Laky-64/
