from dataclasses import dataclass
from warnings import warn

from .info import Info


@dataclass
class Record:
    index: int
    domain: str
    results: dict
    user_info: dict

    def __init__(self, index, domain, **kwargs):
        self.index = index
        self.domain = domain
        self.results = {}
        self.user_info = kwargs

    def append(self, op_info: Info):
        if not op_info:
            return self

        op = op_info.op_name
        if op in self.results:
            warn(f"overwriting result from operation {op}")
        self.results[op] = op_info

        return self

    @property
    def __dict__(self):
        ret = {
            "index": self.index,
            "domain": self.domain,
            **self.user_info,
        }

        for op_name, res in self.results.items():
            info = {
                f"{op_name}_{key}": value
                for key, value in vars(res).items()
            }
            ret = {**ret, **info}

        return ret
