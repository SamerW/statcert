from abc import ABC, abstractmethod, abstractstaticmethod

from .record import Record


class Operation(ABC):
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, tb):
        return

    @abstractstaticmethod
    def prepare_entry(record: Record) -> dict:
        ...

    @abstractmethod
    async def execute(self, **kwargs) -> list:
        ...
