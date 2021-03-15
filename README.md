<p align="center">
  <img src="https://user-images.githubusercontent.com/32808683/111091141-62473b00-8508-11eb-9c05-3e0fd4a21af3.png" alt="pytgcalls logo" />
</p>

# PyTgCalls

[![pre-commit.ci status][pre-commit.ci-badge]][pre-commit.ci]

This project allow to make Telegram group call with MTProto Api using Program and WebRTC, this is possible thanks to the power of NodeJS's WebRTC library, socketio-client and [@evgeny-nadymov]

## Docs

[Read the docs!][docs]

## How to install?

Here's how to install the PyTgCalls lib, the commands are given below:

``` bash
# With Git
pip install git+https://github.com/pytgcalls/pytgcalls

# With PyPi
pip install py-tgcalls
```

## Conversion commands

From file to raw format
``` bash
ffmpeg -i {INPUT_FILE} -f s16le -ac 1 -acodec pcm_s16le -ar {BITRATE} {OUTPUT_FILE}
```

From stream link to raw format
``` bash
ffmpeg -y -i {STREAM_LINK} -f s16le -ac 1 -acodec pcm_s16le -ar {BITRATE} {OUTPUT_FILE}
```

From youtube video/live-stream to raw format
``` bash
ffmpeg -i "$(youtube-dl -x -g "{YOUTUBE_LINK}")" -f s16le -ac 1 -acodec pcm_s16le -ar {BITRATE} {OUTPUT_FILE}
```

## Credits

Big thanks to [@evgeny-nadymov] for allowing us to use their code from [telegram-react]

This library is based on [tgcallsjs] developed [@AndrewLaneX] and pyservercall by [@Laky-64]

[pre-commit.ci-badge]: https://results.pre-commit.ci/badge/github/pytgcalls/pytgcalls/master.svg
[pre-commit.ci]: https://results.pre-commit.ci/latest/github/pytgcalls/pytgcalls/master
[docs]: https://pytgcalls.github.io/
[@evgeny-nadymov]: https://github.com/evgeny-nadymov/
[@AndrewLaneX]: https://github.com/AndrewLaneX/
[telegram-react]: https://github.com/evgeny-nadymov/telegram-react/
[tgcallsjs]: https://github.com/tgcallsjs/tgcalls
[pyservercall]: https://github.com/pytgcalls/pyservercall/
[@Laky-64]: https://github.com/Laky-64/
