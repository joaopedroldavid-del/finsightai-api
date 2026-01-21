from abc import ABC, abstractmethod
from typing import Any

class BaseAgent(ABC):

    @abstractmethod
    async def initialize(self) -> Any:
        pass

    @abstractmethod
    def get_agent_type(self) -> str:
        pass