from abc import ABC, abstractmethod
import asyncio

class IScraper(ABC):
    @abstractmethod
    def nombre(self) -> str:
        pass

    @abstractmethod
    async def extraer(self, queue: asyncio.Queue):
        pass
