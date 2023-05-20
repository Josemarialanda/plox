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
        self.__declaration = declaration
        self.__closure = closure
        self.__isInitializer = isInitializer

    def __str__(self) -> str:
        return f"< fn {self.__declaration.name.lexeme} >"

    def arity(self) -> int:
        return len(self.__declaration.params)

    def bind(self, instance: PloxInstance) -> "PloxFunction":
        environment = Environment(self.__closure)
        environment.define("this", instance)
        return PloxFunction(self.__declaration, environment, self.__isInitializer)

    def call(self, interpreter, arguments: list[Any]) -> Any:
        environment = Environment(self.__closure)
        for i in range(len(self.__declaration.params)):
            environment.define(self.__declaration.params[i].lexeme, arguments[i])
        try:
            interpreter.executeBlock(self.__declaration.body, environment)
        except PloxReturnException as ploxReturnException:
            if self.__isInitializer:
                return self.__closure.getAt(0, "this")
            return ploxReturnException.value
