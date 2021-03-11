from typing import Any
from abc import ABC, abstractmethod


class BrokerInterface(ABC):
    @abstractmethod
    async def init_broker(self): ...

    @abstractmethod
    async def send(self, *, channel_name: str, **kwargs): ...

    @abstractmethod
    async def listen(self, *, channel_name: str, **kwargs): ...

    @abstractmethod
    async def get_result(self, key) -> Any: ...

    @abstractmethod
    async def channel_cleanup(self): ...

    @abstractmethod
    async def close(self): ...
