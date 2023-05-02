from parser.stmt import Stmt


class Resolver:
    def __init__(self, program: list[Stmt]) -> None:
        self.__hadError = False
        self.__resolvedProgram = program

    @property
    def resolvedProgram(self) -> list[Stmt]:
        return self.__resolvedProgram

    @property
    def hadError(self) -> bool:
        return self.__hadError

    def run(self):
        pass
