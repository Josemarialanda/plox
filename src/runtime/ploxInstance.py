from scanner.token import Token
from runtime.ploxRuntimeError import PloxRuntimeError


class PloxInstance:
    def __init__(self, klass):
        self.__klass = klass
        self.__fields = {}

    def __str__(self) -> str:
        return self.__klass.name + " instance"

    def getAttr(self, name: Token) -> object:
        if name.lexeme in self.__fields:
            return self.__fields[name.lexeme]

        method = self.__klass.findMethod(name.lexeme)
        if method is not None:
            return method.bind(self)
        raise PloxRuntimeError(name, f"Undefined property {name.lexeme}.")

    def setAttr(self, name: Token, value: object) -> None:
        self.__fields[name.lexeme] = value
