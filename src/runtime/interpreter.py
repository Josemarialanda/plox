from parser.stmt import Stmt
from typing import Any


class Interpreter:
    def __init__(self, program: list[Stmt]) -> None:
        self.__hadError = False
        self.__result = program

    @property
    def result(self) -> Any:
        return self.__result

    @property
    def hadError(self) -> bool:
        return self.__hadError

    def run(self):
        pass
