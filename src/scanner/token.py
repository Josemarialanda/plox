from typing import Optional
from scanner.tokenType import TokenType

class Token:
  def __init__(self
              ,tokenType: TokenType
              ,lexeme   : str
              ,literal  : Optional[str|float]
              ) -> None:
    self.tokenType = tokenType
    self.lexeme    = lexeme
    self.literal   = literal

  def __str__( self ) -> str:
    return f'''
    type    = {self.tokenType} 
    lexeme  = {self.lexeme} 
    literal = {self.literal}
    '''