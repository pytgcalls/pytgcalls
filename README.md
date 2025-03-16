<img src="https://raw.githubusercontent.com/pytgcalls/pytgcalls/master/.github/images/banner.png" alt="pytgcalls logo" />
<p align="center">
    <b>A simple and elegant client that allows you to make group voice calls quickly and easily.</b>
    <br>
    <a href="https://github.com/pytgcalls/pytgcalls/tree/master/example">
        Examples
    </a>
    •
    <a href="https://pytgcalls.github.io/">
        Documentation
    </a>
    •
    <a href="https://pypi.org/project/py-tgcalls/">
        PyPi
    </a>
    •
    <a href="https://t.me/pytgcallsnews">
        Channel
    </a>
    •
    <a href="https://t.me/pytgcallschat">
        Chat
    </a>
</p>

# PyTgCalls [![PyPI](https://img.shields.io/pypi/v/py-tgcalls.svg?logo=python&logoColor=%23959DA5&label=pypi&labelColor=%23282f37)](https://pypi.org/project/py-tgcalls/) [![Downloads](https://img.shields.io/pepy/dt/py-tgcalls?logoColor=%23959DA5&labelColor=%23282f37&color=%2328A745)](https://pepy.tech/project/py-tgcalls)
This project allows making Telegram call using MtProto and WebRTC, this is possible thanks to the power of [NTgCalls] library and [@evgeny-nadymov]

#### Example Usage
```python
from pytgcalls import PyTgCalls
from pytgcalls import idle
...
chat_id = -1001185324811
app = PyTgCalls(client)
app.start()
app.play(
    chat_id,
    'http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4',
)
idle()
```

## Features
- Prebuilt wheels for macOS, Linux and Windows.
- Supporting all type of MTProto libraries: Pyrogram, Telethon and Hydrogram.
- Work with voice chats in channels and chats.
- Join as channels or chats.
- Mute/unmute, pause/resume, stop/play, volume control and more...

## Requirements
- Python 3.9 or higher.
- An MTProto Client
- A [Telegram API key](https://docs.pyrogram.org/intro/setup#api-keys).

## How to install?
Here's how to install the PyTgCalls lib, the commands are given below:

``` bash
# With Git
pip install git+https://github.com/pytgcalls/pytgcalls -U

# With PyPi (Recommended)
pip install py-tgcalls -U
```

## Key Contributors
* <b><a href="https://github.com/Laky-64">@Laky-64</a> (DevOps Engineer, Software Architect):</b>
    * Played a crucial role in developing PyTgCalls being an ex developer of pyservercall and of tgcallsjs.
    * Automation with GitHub Actions
* <b><a href="https://github.com/kuogi">@kuogi</a> (Senior UI/UX designer, Documenter):</b>
    * As a Senior UI/UX Designer, Kuogi has significantly improved the user interface of our documentation,
      making it more visually appealing and user-friendly.
    * Played a key role in writing and structuring our documentation, ensuring that it is clear,
      informative, and accessible to all users.
* <b><a href="https://github.com/vrumger">@vrumger</a> (Senior Node.js Developer, Software Architect):</b>
    * Has made important fixes and enhancements to the WebRTC component of the library,
      improving its stability and performance.
    * Main developer of TgCallsJS
* <b><a href="https://github.com/alemidev">@alemidev</a> (Senior Python Developer):</b>
    * Has made important fixes and enhancements to the async part of the library

## Junior Developers
* <b><a href="https://github.com/TuriOG">@TuriOG</a> (Junior Python Developer):</b>
    * Currently working on integrating NTgCalls into <a href="//github.com/pytgcalls/pytgcalls">PyTgCalls</a>, an important step
      in expanding the functionality and usability of the library.

## Special Thanks
* <b><a href="https://github.com/evgeny-nadymov">@evgeny-nadymov</a>:</b>
  A heartfelt thank you to Evgeny Nadymov for graciously allowing us to use their code from telegram-react.
  His contribution has been pivotal to the success of this project.

[NTgCalls]: https://github.com/pytgcalls/ntgcalls
[@evgeny-nadymov]: https://github.com/evgeny-nadymov/
