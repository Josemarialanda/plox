from scanner.token import Token
from runtime.ploxRuntimeError import PloxRuntimeError
from typing import Optional

PloxObject = Optional[bool|str|float]

class Environment:
    def __init__(self, enclosing: 'Optional[Environment]' = None):
        self.enclosing = enclosing
        self.values: dict[str, PloxObject] = {}

    def define(self, name: str, value: PloxObject):
        self.values[name] = value
        
    def get(self, name: Token) -> PloxObject:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing:
            return self.enclosing.get(name)
        raise PloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
    
    def assign(self, name: Token, value: PloxObject):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        raise PloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")