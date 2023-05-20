import time
from runtime.ploxCallable import PloxCallable


class Clock(PloxCallable):
    def call(self, interpreter, arguments) -> float:
        return time.time()

    def arity(self) -> int:
        return 0

    def __str__(self) -> str:
        return "<native fn>"


class CurrentTime(PloxCallable):
    def call(self, interpreter, arguments) -> str:
        return time.ctime()

    def arity(self) -> int:
        return 0

    def __str__(self) -> str:
        return "<native fn>"


functions = {"time": Clock(), "currentTime": CurrentTime()}
