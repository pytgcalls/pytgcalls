<img src="https://raw.githubusercontent.com/pytgcalls/pytgcalls/master/.github/images/banner.png" alt="pytgcalls logo" />

<p align="center">
    <b>A simple and elegant client that allows you to make group voice calls quickly and easily. 🎧📞</b>
    <br>
    <a href="https://github.com/pytgcalls/pytgcalls/tree/master/example">
        🔹 Examples
    </a> •
    <a href="https://pytgcalls.github.io/">
        📚 Documentation
    </a> •
    <a href="https://pypi.org/project/py-tgcalls/">
        🛠️ PyPi
    </a> •
    <a href="https://t.me/pytgcallsnews">
        📢 Channel
    </a> •
    <a href="https://t.me/pytgcallschat">
        💬 Chat
    </a>
</p>

# PyTgCalls
[![PyPI](https://img.shields.io/pypi/v/py-tgcalls.svg?logo=python&logoColor=%23959DA5&label=pypi&labelColor=%23282f37)](https://pypi.org/project/py-tgcalls/)
[![Downloads](https://img.shields.io/pepy/dt/py-tgcalls?logoColor=%23959DA5&labelColor=%23282f37&color=%2328A745)](https://pepy.tech/project/py-tgcalls)

PyTgCalls enables the creation of Telegram voice calls using the MtProto protocol and WebRTC, made possible thanks to the powerful [NTgCalls] library and [@evgeny-nadymov]. 🚀

#### Example Usage
```python
from pytgcalls import PyTgCalls
from pytgcalls import idle
from pytgcalls.types import MediaStream
...
chat_id = -1001185324811
app = PyTgCalls(client)
app.start()
app.play(
    chat_id,
    MediaStream(
        'http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4',
    )
)
idle()
```

## Features 🌟
- Prebuilt wheels for macOS, Linux, and Windows.
- Full support for all types of MTProto libraries: Pyrogram, Telethon, and Hydrogram.
- Work with voice chats in channels and chats.
- Extensive controls: mute/unmute, pause/resume, stop/play, volume adjustments, and more...

## Requirements 🛠️
- Python 3.8 or higher.
- An MTProto Client (e.g., Pyrogram, Telethon).
- A [Telegram API key](https://docs.pyrogram.org/intro/setup#api-keys).

## Installation Instructions ⚙️

To install the PyTgCalls library, follow these commands:

```bash
# With Git
pip install git+https://github.com/pytgcalls/pytgcalls -U

# With PyPi (Recommended)
pip install py-tgcalls -U
```

## Key Contributors 👨‍💻

* <b><a href="https://github.com/Laky-64">@Laky-64</a> (DevOps Engineer, Software Architect):</b>
    - Key figure in developing PyTgCalls, former developer of pyservercall and tgcallsjs.
    - Pioneered automation using GitHub Actions.

* <b><a href="https://github.com/kuogi">@kuogi</a> (Senior UI/UX Designer, Documenter):</b>
    - Enhanced the UI/UX of our documentation, making it visually appealing and easy to use.
    - Played a major role in writing and organizing clear, informative documentation.

* <b><a href="https://github.com/vrumger">@vrumger</a> (Senior Node.js Developer, Software Architect):</b>
    - Made crucial fixes and optimizations to the WebRTC component, enhancing performance and stability.
    - Lead developer of TgCallsJS.

* <b><a href="https://github.com/alemidev">@alemidev</a> (Senior Python Developer):</b>
    - Significant contributions to the asynchronous part of the library, improving its efficiency.

## Junior Developers 🌱

* <b><a href="https://github.com/TuriOG">@TuriOG</a> (Junior Python Developer):</b>
    - Currently working on integrating NTgCalls into <a href="//github.com/pytgcalls/pytgcalls">PyTgCalls</a>, expanding functionality and usability.

## Special Thanks 🙏

* <b><a href="https://github.com/evgeny-nadymov">@evgeny-nadymov</a>:</b>
  - A special thank you to Evgeny Nadymov for generously sharing their code from telegram-react, a key contribution to this project's success.

[NTgCalls]: https://github.com/pytgcalls/ntgcalls
[@evgeny-nadymov]: https://github.com/evgeny-nadymov/
