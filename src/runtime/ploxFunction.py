from runtime.ploxCallable import PloxCallable
from runtime.ploxInstance import PloxInstance
from runtime.ploxReturnException import PloxReturnException
from runtime.environment import Environment
from parser import stmt
from typing import Any


class PloxFunction(PloxCallable):
    def __init__(
        self, declaration: stmt.Function, closure: Environment, isInitializer: bool
    ):
        self.declaration = declaration
        self.closure = closure
        self.isInitializer = isInitializer

    def arity(self) -> int:
        return len(self.declaration.params)

    def bind(self, instance: PloxInstance) -> "PloxFunction":
        environment = Environment(self.closure)
        environment.define("this", instance)
        return PloxFunction(self.declaration, environment, self.isInitializer)

    def call(self, interpreter, arguments: list[Any]) -> Any:
        environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except PloxReturnException as ploxReturnException:
            if self.isInitializer:
                return self.closure.getAt(0, "this")
            return ploxReturnException.value

    def __str__(self) -> str:
        return f"< fn {self.declaration.name.lexeme} >"
