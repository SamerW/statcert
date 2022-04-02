

from abc import ABC, abstractmethod, abstractclassmethod
from dataclasses import dataclass


class Info(ABC):  # not serializable
    @property
    @abstractclassmethod
    def op_name(cls) -> str:
        ...

    @property
    @abstractmethod
    def __dict__(self) -> dict:  # serializable
        ...


@dataclass
class ProbeInfo(Info):
    op_name = "probe"

    status: str
    home_page: str
    redirected: bool
    attempts: int
    errors: list
    reason: str

    @property
    def __dict__(self):
        return {
            "status": self.status,
            "home_page": self.home_page,
            "redirected": self.redirected,
            "attempts": self.attempts,
            "errors": self.errors,
            "reason": self.reason,
        }


@dataclass
class OCSPInfo(Info):
    op_name = "ocsp"

    status: str

    @property
    def __dict__(self):
        return {
            "status": self.status
        }
