from parser.stmt import Stmt


class Resolver:
    def __init__(self, program: list[Stmt], runtime):
        self.__runtime = runtime
        self.__resolvedProgram = program

    @property
    def resolvedProgram(self) -> list[Stmt]:
        return self.__resolvedProgram

    def run(self):
        pass
