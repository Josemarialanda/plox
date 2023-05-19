from scanner.token import Token
from runtime.ploxRuntimeError import PloxRuntimeError
from typing import Optional, Any


class Environment:
    def __init__(self, enclosing: "Optional[Environment]" = None):
        self.enclosing = enclosing
        self.values: dict[str, Any] = {}

    def define(self, name: str, value: Any):
        self.values[name] = value

    def __ancestor(self, distance: int) -> "Environment":
        environment: "Environment" = self
        for _ in range(distance):
            if enclosing := environment.enclosing:
                environment = enclosing
        return environment

    def getAt(self, distance: int, name: str) -> Any:
        """
        Return a variable at a distance
        """
        if ancestor := self.__ancestor(distance):
            return ancestor.values.get(name)

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing:
            return self.enclosing.get(name)
        raise PloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        raise PloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assignAt(self, distance: int, name: Token, value: Any):
        self.__ancestor(distance).values[name.lexeme] = value
