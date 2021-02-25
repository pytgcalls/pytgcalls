# PyTgCalls

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/pytgcalls/pytgcalls/master.svg)](https://results.pre-commit.ci/latest/github/pytgcalls/pytgcalls/master)

# Installation

Follow the steps below to install PyTgCalls without facing problems:

1. Clone the repository.
2. If you are not too much skilled in NodeJS or don't have it installed in your machine, the recommended way to install is using [nodesource.com](https://nodesource.com).
3. Change current dir to the clone folder:
   ```bash
   cd pytgcalls/
   ```
4. Run the following commands to install the NodeJS requirements:
   ```bash
   npm install && \
   npm run prepare && \
   cd pytgcalls/js && \
   npm install && \
   cd ../../
   ```
5. Install Python requirements:
   ```bash
   pip install requirements.txt
   ```
6. Remove the `.git` folder:
   ```bash
   sudo rm -r .git
   ```
7. Move the folder to `site-packages` for easier access:
   ```bash
   cd ../ && \
   mv pytgcalls ~/.local/lib/python3.*/site-package
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
