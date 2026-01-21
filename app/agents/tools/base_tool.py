from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        pass