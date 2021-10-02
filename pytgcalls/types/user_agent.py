from typing import List
from typing import Optional


class AgentInfo:
    def __init__(
        self,
        name: str,
        version: str,
        device: Optional[str] = None,
        os_name: Optional[str] = None,
        arch_type: Optional[str] = None,
    ):
        self.name: str = name
        self.version: str = version
        self.device: Optional[str] = device
        self.os_name: Optional[str] = os_name
        self.arch_type: Optional[str] = arch_type


class UserAgent:
    def __init__(
        self,
        user_agents: List[AgentInfo],
    ):
        self.user_agents: List[AgentInfo] = user_agents

    def __str__(self):
        return ' '.join([
            f'{user_agent.name}/{user_agent.version}'
            ' (' + '; '.join(
                filter(
                    bool, [
                        user_agent.device,
                        user_agent.os_name,
                        user_agent.arch_type,
                    ],
                ),
            ) + ');'
            for user_agent in self.user_agents
        ]).replace(' ()', '')
