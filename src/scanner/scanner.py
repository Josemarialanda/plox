from typing import Optional

from scanner.token import Token
from scanner.tokenType import TokenType


class Scanner:
    def __init__(self, source):
        self.__hasError: bool = False
        self.__source: str = source
        self.__tokens: list[Token] = []
        self.__start: int = 0
        self.__current: int = 0
        self.__line: int = 1
        self.__column: int = 1

    __keywords = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
        "assert": TokenType.ASSERT,
    }

    def run(self) -> None:
        self.__scanTokens()

    @property
    def tokens(self) -> list[Token]:
        if self.__hasError:
            return []
        return self.__tokens

    @property
    def hasError(self) -> bool:
        return self.__hasError

    def __scanTokens(self) -> None:
        while not self.__isEOF():
            self.__scanToken()
        self.__eof()

    def __scanToken(self) -> None:
        self.__start = self.__current
        char = self.__advance()
        match char:
            case None:
                pass
            case "(":
                self.__addToken(TokenType.LEFT_PAREN)
            case ")":
                self.__addToken(TokenType.RIGHT_PAREN)
            case "{":
                self.__addToken(TokenType.LEFT_BRACE)
            case "}":
                self.__addToken(TokenType.RIGHT_BRACE)
            case ",":
                self.__addToken(TokenType.COMMA)
            case ".":
                self.__addToken(TokenType.DOT)
            case "-":
                self.__addToken(TokenType.MINUS)
            case "+":
                self.__addToken(TokenType.PLUS)
            case ";":
                self.__addToken(TokenType.SEMICOLON)
            case "*":
                self.__addToken(TokenType.STAR)
            case "%":
                self.__addToken(TokenType.PERCENT)
            case "!":
                self.__addToken(
                    TokenType.BANG_EQUAL if self.__match("=") else TokenType.BANG
                )
            case "=":
                self.__addToken(
                    TokenType.EQUAL_EQUAL if self.__match("=") else TokenType.EQUAL
                )
            case "<":
                self.__addToken(
                    TokenType.LESS_EQUAL if self.__match("=") else TokenType.LESS
                )
            case ">":
                self.__addToken(
                    TokenType.GREATER_EQUAL if self.__match("=") else TokenType.GREATER
                )
            case " " | "\r" | "\t" | "\n":
                pass
            case '"':
                self.__string()
            case "/":
                if self.__match("/"):
                    while self.__peek() != "\n" and not self.__isEOF():
                        self.__advance()
                elif self.__match("*"):
                    self.__blockComment()
                else:
                    self.__addToken(TokenType.SLASH)
            case _:
                if char.isdigit():
                    self.__number()
                elif self.isIdentifierPart(char):
                    self.__identifier()
                else:
                    self.__error(f"Unexpected character '{char}'")
        return

    def __blockComment(self) -> None:
        while self.__peek() + self.__peekNext() != "*/":
            self.__advance()
            if self.__isEOF():
                self.__advance()
                self.__error("Unterminated block comment")
                break
        self.__advance()
        self.__advance()

    def __string(self) -> None:
        while self.__peek() != '"' and not self.__isEOF():
            self.__advance()
        if self.__isEOF():
            self.__error("Unterminated string")
            return
        self.__advance()
        literal = self.__source[self.__start + 1 : self.__current - 1]
        self.__addToken(TokenType.STRING, literal)

    def __number(self) -> None:
        while self.__peek().isdigit():
            self.__advance()
        if self.__peek() == "." and self.__peekNext().isdigit():
            self.__advance()
            while self.__peek().isdigit():
                self.__advance()
        self.__addToken(
            TokenType.NUMBER, float(self.__source[self.__start : self.__current])
        )

    def __eof(self) -> None:
        self.__tokens.append(Token(TokenType.EOF, "", None))

    def __identifier(self) -> None:
        while self.isIdentifierPart(self.__peek()):
            self.__advance()
        text = self.__source[self.__start : self.__current]
        self.__addToken(self.__keywords.get(text, TokenType.IDENTIFIER))

    @staticmethod
    def isIdentifierPart(c: str):
        return c.replace("_", "a").isalnum()

    def __match(self, expected: str) -> bool:
        if self.__source[self.__current] != expected or self.__isEOF():
            return False
        self.__advance()
        return True

    def __peek(self) -> str:
        if self.__isEOF():
            return "\0"
        return self.__source[self.__current]

    def __peekNext(self) -> str:
        if self.__current + 1 >= len(self.__source):
            return "\0"
        return self.__source[self.__current + 1]

    def __advance(self) -> str:
        current = self.__peek()
        match current:
            case "\n":
                self.__line += 1
                self.__column = 1
            case _:
                self.__column += 1
        self.__current += 1
        return current

    def __addToken(
        self, type: TokenType, literal: Optional[float | str] = None
    ) -> None:
        text = self.__source[self.__start : self.__current]
        self.__tokens.append(Token(type, text, literal))

    def __error(self, message: str) -> None:
        self.__hasError = True
        print(
            f"""
      line : {self.__line}
      column : {self.__column-1}
      {message}
      """
        )

    def __isEOF(self) -> bool:
        return self.__current >= len(self.__source)
