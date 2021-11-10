from .user_agent import AgentInfo
from .user_agent import UserAgent


class Browsers:
    def __init__(self):
        # CHROME BASE AGENT
        self._chrome_agent = AgentInfo(
            'Chrome',
            '94.0.4606.71',
        )

        # MOZILLA BASE AGENTS
        self._mozilla_android_agent = AgentInfo(
            'Mozilla',
            '5.0',
            'Linux',
            'Android 10',
        )
        self._mozilla_ios_agent = AgentInfo(
            'Mozilla',
            '5.0',
            'iPhone',
            'CPU iPhone OS 15_0 like Mac OS X',
        )
        self._mozilla_linux_agent = AgentInfo(
            'Mozilla',
            '5.0',
            'X11',
            'Linux x86_64',
        )
        self._mozilla_macos_agent = AgentInfo(
            'Mozilla',
            '5.0',
            'Macintosh',
            'Intel Mac OS X 11_6',
        )
        self._mozilla_windows_agent = AgentInfo(
            'Mozilla',
            '5.0',
            'Windows NT 10.0',
            'Win64',
            'x64',
        )

        # APPLE_WEBKIT BASE AGENT
        self._apple_webkit_agent = AgentInfo(
            'AppleWebKit',
            '537.36',
            'KHTML',
            'like Gecko',
        )
        self._apple_webkit_apple_agent = AgentInfo(
            'AppleWebKit',
            '605.1.15',
            'KHTML',
            'like Gecko',
        )

        # SAFARI BASE AGENT
        self._safari_agent = AgentInfo(
            'Safari',
            '537.36',
        )
        self._safari_mobile_agent = AgentInfo(
            'Mobile Safari',
            '537.36',
        )
        self._safari_macos_agent = AgentInfo(
            'Safari',
            '605.1.15',
        )
        self._safari_ios_agent = AgentInfo(
            'Safari',
            '604.1',
        )

        # EDGE BASE AGENT
        self._edge_android_agent = AgentInfo(
            'EdgA',
            '93.0.961.53',
        )
        self._edge_ios_agent = AgentInfo(
            'EdgiOS',
            '93.961.64',
        )
        self._edge_pc_agent = AgentInfo(
            'Edg',
            '94.0.992.31',
        )
        self._edge_windows_mob_agent = AgentInfo(
            'Edge',
            '40.15254.603',
        )
        self._edge_xbox_agent = AgentInfo(
            'Edge',
            '44.18363.8131',
        )

        # FIREFOX BASE AGENT
        self._firefox_default_agent = AgentInfo(
            'Firefox',
            '92.0',
        )
        self._firefox_ios_agent = AgentInfo(
            'FxiOS',
            '38.0',
        )

        # OPERA BASE AGENT
        self._opera_default_agent = AgentInfo(
            'OPR',
            '79.0.4143.66',
        )
        self._opera_mobile_agent = AgentInfo(
            'OPR',
            '63.3.3216.58675',
        )

    # CHROME
    @property
    def chrome_android(self):
        return str(
            UserAgent([
                self._mozilla_android_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_mobile_agent,
            ]),
        )

    @property
    def chrome_ios(self):
        return str(
            UserAgent([
                self._mozilla_ios_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_agent,
            ]),
        )

    @property
    def chrome_linux(self):
        return str(
            UserAgent([
                self._mozilla_linux_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_agent,
            ]),
        )

    @property
    def chrome_macos(self):
        return str(
            UserAgent([
                self._mozilla_macos_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_agent,
            ]),
        )

    @property
    def chrome_windows(self):
        return str(
            UserAgent([
                self._mozilla_windows_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_agent,
            ]),
        )

    # EDGE
    @property
    def edge_android(self):
        return str(
            UserAgent([
                self._mozilla_android_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_mobile_agent,
                self._edge_android_agent,
            ]),
        )

    @property
    def edge_ios(self):
        return str(
            UserAgent([
                self._mozilla_ios_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_agent,
                self._edge_ios_agent,
            ]),
        )

    @property
    def edge_macos(self):
        return str(
            UserAgent([
                self._mozilla_macos_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_agent,
                self._edge_pc_agent,
            ]),
        )

    @property
    def edge_windows(self):
        return str(
            UserAgent([
                self._mozilla_windows_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_agent,
                self._edge_pc_agent,
            ]),
        )

    @property
    def edge_windows_mobile(self):
        return str(
            UserAgent([
                self._mozilla_windows_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_agent,
                self._edge_windows_mob_agent,
            ]),
        )

    @property
    def edge_xbox_one(self):
        return str(
            UserAgent([
                self._mozilla_windows_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_agent,
                self._edge_xbox_agent,
            ]),
        )

    # FIREFOX
    @property
    def firefox_android(self):
        return str(
            UserAgent([
                self._mozilla_android_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_mobile_agent,
                self._firefox_default_agent,
            ]),
        )

    @property
    def firefox_ios(self):
        return str(
            UserAgent([
                self._mozilla_ios_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_agent,
                self._firefox_ios_agent,
            ]),
        )

    @property
    def firefox_linux(self):
        return str(
            UserAgent([
                self._mozilla_linux_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_agent,
                self._firefox_default_agent,
            ]),
        )

    @property
    def firefox_macos(self):
        return str(
            UserAgent([
                self._mozilla_macos_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_agent,
                self._firefox_default_agent,
            ]),
        )

    @property
    def firefox_windows(self):
        return str(
            UserAgent([
                self._mozilla_windows_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_agent,
                self._firefox_default_agent,
            ]),
        )

    # OPERA
    @property
    def opera_android(self):
        return str(
            UserAgent([
                self._mozilla_android_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_mobile_agent,
                self._opera_mobile_agent,
            ]),
        )

    @property
    def opera_linux(self):
        return str(
            UserAgent([
                self._mozilla_linux_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_agent,
                self._opera_default_agent,
            ]),
        )

    @property
    def opera_macos(self):
        return str(
            UserAgent([
                self._mozilla_macos_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_agent,
                self._opera_default_agent,
            ]),
        )

    @property
    def opera_windows(self):
        return str(
            UserAgent([
                self._mozilla_windows_agent,
                self._apple_webkit_agent,
                self._chrome_agent,
                self._safari_agent,
                self._opera_default_agent,
            ]),
        )

    # SAFARI
    @property
    def safari_ios(self):
        return str(
            UserAgent([
                self._mozilla_ios_agent,
                self._apple_webkit_apple_agent,
                self._chrome_agent,
                self._safari_ios_agent,
            ]),
        )

    @property
    def safari_macos(self):
        return str(
            UserAgent([
                self._mozilla_macos_agent,
                self._apple_webkit_apple_agent,
                self._chrome_agent,
                self._safari_macos_agent,
            ]),
        )
