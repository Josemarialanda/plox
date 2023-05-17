from scanner.token import Token


class PloxRuntimeError(Exception):
    def __init__(self, token: Token, message: str):
        self.token: Token = token
        self.message: str = message
