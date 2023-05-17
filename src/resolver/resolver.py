from parser.stmt import Stmt


class Resolver:
    def __init__(self, runtime):
        pass

    @property
    def resolvedProgram(self) -> list[Stmt]:
        return self.__resolvedProgram

    def run(self, program: list[Stmt]):
        self.__resolvedProgram = program
        pass
