class AgentInfo:
    def __init__(
        self,
        name: str,
        version: str,
        device: str | None = None,
        os_name: str | None = None,
        arch_type: str | None = None,
    ):
        self.name: str = name
        self.version: str = version
        self.device: str | None = device
        self.os_name: str | None = os_name
        self.arch_type: str | None = arch_type


class UserAgent:
    def __init__(
        self,
        user_agents: list[AgentInfo],
    ):
        self.user_agents: list[AgentInfo] = user_agents

    def __str__(self):
        return ' '.join(
            [
                f'{user_agent.name}/{user_agent.version}'
                ' ('
                + '; '.join(
                    filter(
                        bool,
                        [
                            user_agent.device,
                            user_agent.os_name,
                            user_agent.arch_type,
                        ],
                    ),
                )
                + ');'
                for user_agent in self.user_agents
            ]
        ).replace(' ()', '')
