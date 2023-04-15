from enum import Enum

class Lexer:
  
  def __init__(self, source):    
    with open(source, "r") as sourceFile:
      self.source = sourceFile.read()
    self.tokens = []
    self.errors = []
    self.position = 0
    self.line = 1
    self.column = 1
    self.run()
    
  def run(self):
    self.scan()
    if self.errors != []:
      for error in self.errors:
        print(error)
      exit(65)
    else:
      for token in self.tokens:
        print(token)
      exit(0)
      
  def currentChar(self):
    return self.source[self.position]
  
  def prevChar(self):
    return self.source[self.position-1]
      
  def peek(self):
    return self.source[self.position+1]
        
  def isOEF(self):
    return self.position+1 > len(self.source)
    
  def skipWS(self):
    while self.currentChar().strip() == "":
      self.advance(1)
      if self.isOEF(): break
      
  def advance(self,i):
    for _ in range(i):
      if self.currentChar() == "\n": 
        self.line += 1
        self.column = 1
      else:
        self.column += 1
      self.position += 1
      
  def skipComment(self):
    while self.currentChar() != "\n":
      self.advance(1)
      if self.isOEF(): break
      
  def error(self):
    error = Error(self.line, self.column-1, self.prevChar())
    self.errors.append(error)
    
  def EOF(self):
    EOFToken = Token(TokenType.EOF, "$", self.line, self.column)
    self.tokens.append(EOFToken)
      
  def isOneOrTwoCharacterToken(self):
    TTYPE = None
    char = self.currentChar()
    nextChar = self.peek() if not (self.position+1 >= len(self.source)) else ""
    match (char, nextChar):
      case ("(", _)   : TTYPE = TokenType.LEFT_PAREN
      case (")", _)   : TTYPE = TokenType.RIGHT_PAREN
      case ("{", _)   : TTYPE = TokenType.LEFT_BRACE
      case ("}", _)   : TTYPE = TokenType.RIGHT_BRACE
      case (",", _)   : TTYPE = TokenType.COMMA
      case (".", _)   : TTYPE = TokenType.DOT
      case ("-", _)   : TTYPE = TokenType.MINUS
      case ("+", _)   : TTYPE = TokenType.PLUS
      case (";", _)   : TTYPE = TokenType.SEMICOLON
      case ("/", "/") : self.skipComment(); return True
      case ("/", _)   : TTYPE = TokenType.SLASH
      case ("*", _)   : TTYPE = TokenType.STAR
      case (">", "=") : char += nextChar; TTYPE = TokenType.GREATER_EQUAL
      case (">", _)   : TTYPE = TokenType.GREATER
      case ("<", "=") : char += nextChar; TTYPE = TokenType.LESS_EQUAL
      case ("<", _)   : TTYPE = TokenType.LESS
      case ("=", "=") : char += nextChar; TTYPE = TokenType.EQUAL_EQUAL
      case ("=", _)   : TTYPE = TokenType.EQUAL
      case ("!", "=") : char += nextChar; TTYPE = TokenType.BANG_EQUAL
      case ("!", _)   : TTYPE = TokenType.BANG
      case _: char = ""
    if char == "": 
      self.advance(1)
      return False
    self.column += len(char)-1
    token = Token( 
        TTYPE
      , char
      , self.line
      , self.column)
    self.tokens.append(token)
    self.advance(len(char))
    return True
  
  def isLiteral(self):
    pos = self.position
    col = self.column
    lexeme = ""
    
    def advanceLexeme():
      nonlocal pos
      nonlocal col
      nonlocal lexeme
      lexeme += self.source[pos]
      pos += 1
      col += 1
      
    def appendToken(tokenType):
      nonlocal lexeme
      self.tokens.append(Token(
          tokenType 
        , lexeme
        , self.line
        , self.column))
    
    def isString():
      nonlocal pos
      nonlocal lexeme
      if self.source[pos] == '"':
        pos += 1
        while self.source[pos] != '"':
          advanceLexeme()
          if pos+1 > len(self.source): break
        appendToken(TokenType.STRING)
        self.position = pos+1
        self.column = col+1
        return True
      else: return False
  
    def isNumber():
      nonlocal pos
      nonlocal lexeme
      if self.source[pos].isdigit():
        while self.source[pos].isdigit():
          advanceLexeme()
          if pos+1 > len(self.source): break
        appendToken(TokenType.NUMBER)
        self.position = pos+1
        self.column = col+1
        return True
      else: return False
      
    def isIdentifier():
      nonlocal pos
      nonlocal lexeme
      if self.source[pos].isalpha():
        while self.source[pos].isalnum() or self.source[pos] == "_":
          advanceLexeme()
          if pos+1 > len(self.source): break
        if keywords.get(lexeme) is not None: appendToken(keywords[lexeme])
        else                   : appendToken(TokenType.IDENTIFIER)
        self.position = pos+1
        self.column = col+1
        return True
      else: return False 
      
    return (isString() or isNumber() or isIdentifier())
  
  def scan(self):
    while not self.isOEF():
      self.skipWS()
      if self.isOEF(): break
      if not (self.isLiteral() or self.isOneOrTwoCharacterToken()): self.error()
    self.EOF()
    
class TokenType(Enum):    
  # Single-character tokens.
  LEFT_PAREN = 1; RIGHT_PAREN = 2; LEFT_BRACE = 3; RIGHT_BRACE = 4
  COMMA = 5; DOT = 6; MINUS = 7; PLUS = 8; 
  SEMICOLON = 9; SLASH = 10; STAR = 11
  
  # One or two character tokens.
  BANG = 12; BANG_EQUAL = 13; EQUAL = 14; EQUAL_EQUAL = 15
  GREATER = 16; GREATER_EQUAL = 17; LESS = 18; LESS_EQUAL = 19
  
  # Literals.
  IDENTIFIER = 20; STRING = 21; NUMBER = 22
  
  # Keywords.
  AND = 23; CLASS = 24; ELSE = 25; FALSE = 26; FUN = 27; FOR = 28; IF = 29
  NIL = 30; OR = 31; PRINT = 32; RETURN = 33; SUPER = 34; THIS = 35; TRUE = 36 
  VAR = 37; WHILE = 38
  
  EOF = 39

keywords = {
  "and"    :  TokenType.AND,
  "class"  :  TokenType.CLASS,
  "else"   :  TokenType.ELSE, 
  "false"  :  TokenType.FALSE,
  "for"    :  TokenType.FOR,
  "fun"    :  TokenType.FUN,
  "if"     :  TokenType.IF,
  "nil"    :  TokenType.NIL,
  "or"     :  TokenType.OR,
  "print"  :  TokenType.PRINT,
  "return" :  TokenType.RETURN,
  "super"  :  TokenType.SUPER,
  "this"   :  TokenType.THIS,
  "true"   :  TokenType.TRUE,
  "var"    :  TokenType.VAR,
  "while"  :  TokenType.WHILE,
}
  
class Token:
  def __init__(self, type, lexeme, line, column):
    self.type = type
    self.lexeme = lexeme
    self.line = line
    self.column = column
  
  def __repr__(self):
    return f'''
      type : {self.type.name}
      lexeme : {self.lexeme}
      line : {self.line}
      column : {self.column}
      '''
  
class Error:  
  def __init__(self, line, column, token):
    self.line = line
    self.column = column
    self.token = token
      
  def __repr__(self):
    return f'''
      Unexpected character "{self.token}"
      line : {self.line}
      column : {self.column}
      '''