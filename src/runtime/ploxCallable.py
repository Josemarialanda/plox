from abc import ABC
from typing import Any


class PloxCallable(ABC):
    def arity(self):
        raise NotImplementedError

    def call(self, interpreter, arguments: list[Any]):
        raise NotImplementedError
