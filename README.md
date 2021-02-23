# PyTgCalls

# How to install?
Here's how to install the PyTgCalls lib, the commands are given below:

``` bash
cd pytgcalls
npm install
npm run prepare
cd pytgcalls
npm install
pip install python-socketio
pip install Naked
pip install aiohttp
pip install asyncio
```

# Command conversion
``` bash
ffmpeg -i {INPUT_FILE} -f s16le -ac 1 -acodec pcm_s16le -ar {BITRATE} {OUTPUT_FILE}
```

## Credits

Big thanks to [@evgeny-nadymov] for allowing us to use their code from [telegram-react]

This library is based on [tgcallsjs] under developing by [@AndrewLaneX] and by [pyservercall] developed by [@Laky-64]

[@evgeny-nadymov]: https://github.com/evgeny-nadymov/
[@AndrewLaneX]: https://github.com/AndrewLaneX/
[telegram-react]: https://github.com/evgeny-nadymov/telegram-react/
[tgcallsjs]: https://github.com/tgcallsjs/tgcalls
[pyservercall]: https://github.com/pytgcalls/pyservercall/
[@Laky-64]: https://github.com/Laky-64/