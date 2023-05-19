from runtime.ploxCallable import PloxCallable
from runtime.ploxFunction import PloxFunction
from runtime.ploxInstance import PloxInstance
from typing import Optional, Any


class PloxClass(PloxCallable):
    def __init__(self, name: str, superclass: 'PloxClass', methods: dict[str, PloxFunction]):
        self.name = name
        self.methods = methods
        self.superclass = superclass

    def call(self, interpreter, arguments: list[Any]):
        instance = PloxInstance(self)
        initializer = self.findMethod("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def arity(self) -> int:
        initializer = self.findMethod("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def findMethod(self, name: str) -> Optional[PloxFunction]:
        if name in self.methods:
            return self.methods[name]
        if self.superclass is not None:
            return self.superclass.findMethod(name)
        
    def __str__(self) -> str:
        return self.name