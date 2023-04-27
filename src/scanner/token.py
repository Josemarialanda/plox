from typing import Optional

from scanner.tokenType import TokenType


class Token:
    def __init__(
        self, tokenType: TokenType, lexeme: str, literal: Optional[str | float]
    ) -> None:
        self.tokenType = tokenType
        self.lexeme = lexeme
        self.literal = literal

    def __str__(self) -> str:
        match (self.tokenType, self.literal):
            case (TokenType.EOF, _):
                return f"""
        {self.tokenType}
        """
            case (_, None):
                return f"""
        type    = {repr(self.tokenType)} 
        lexeme  = {self.lexeme}
        """
            case (_, _):
                return f"""
        type    = {repr(self.tokenType)} 
        lexeme  = {self.lexeme}
        literal = {self.literal}
        """
