from scanner.token import Token
from runtime.ploxRuntimeError import PloxRuntimeError


class PloxInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def __str__(self) -> str:
        return self.klass.name + " instance"

    def getAttr(self, name: Token) -> object:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.findMethod(name.lexeme)
        if method is not None:
            return method.bind(self)
        raise PloxRuntimeError(name, f"Undefined property {name.lexeme}.")

    def setAttr(self, name: Token, value: object) -> None:
        self.fields[name.lexeme] = value
