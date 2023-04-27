"""
Context-Free Grammar:

program        → declaration* eof ;

declaration    → classDecl
               | funDecl
               | varDecl
               | statement ;

classDecl      → "class" IDENTIFIER ( "<" IDENTIFIER )?
                 "{" function* "}" ;

funDecl        → "fun" function ;
function       → IDENTIFIER "(" parameters? ")" block ;
parameters     → IDENTIFIER ( "," IDENTIFIER )* ;

varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;

statement      → exprStmt
               | forStmt
               | ifStmt
               | printStmt
               | returnStmt
               | whileStmt
               | block ;

returnStmt     → "return" expression? ";" ;

forStmt        → "for" "(" ( varDecl | exprStmt | ";" )
                           expression? ";"
                           expression? ")" statement ;

whileStmt      → "while" "(" expression ")" statement ;

ifStmt         → "if" "(" expression ")" statement ( "else" statement )? ;

block          → "{" declaration* "}" ;

exprStmt       → expression ";" ;
printStmt      → "print" expression ";" ;

expression     → assignment ;
assignment     → ( call "." )? IDENTIFIER "=" assignment
               | logic_or;
logic_or       → logic_and ( "or" logic_and )* ;
logic_and      → equality ( "and" equality )* ;
equality       → comparison ( ( "!=" | "==" ) comparison )* ;
comparison     → addition ( ( ">" | ">=" | "<" | "<=" ) addition )* ;
addition       → multiplication ( ( "-" | "+" ) multiplication )* ;
multiplication → unary ( ( "/" | "*" ) unary )* ;
unary          → ( "!" | "-" ) unary | call ;
call           → primary ( "(" arguments? ")" | "." IDENTIFIER )* ;
arguments      → expression ( "," expression )* ;
primary        → "true" | "false" | "nil" | "this"
               | NUMBER | STRING | IDENTIFIER | "(" expression ")"
               | "super" "." IDENTIFIER ;
"""

from parser.expr import (Assign, Binary, Call, Expr, Get, Grouping, Literal,
                         Logical, Set, Super, This, Unary, Variable)
from parser.parserError import ParseError
from parser.stmt import (Block, Class, Expression, Function, If, Print, Return,
                         Stmt, Var, While)
from typing import Optional

from scanner.token import Token
from scanner.tokenType import TokenType


class Parser:
    def __init__(self, tokens: list[Token], onError) -> None:
        self.__hasError: bool = False
        self.__tokens: list[Token] = tokens
        self.__current: int = 0
        self.__program: list[Stmt] = []
        self.onError = onError

    @property
    def hasError(self) -> bool:
        return self.__hasError

    def run(self):
        self.__PROGRAM()

    def __PROGRAM(self):
        return

    def __DECLARATION(self):
        return

    def __CLASS_DECL(self):
        return

    def __FUN_DECL(self):
        return

    def __FUNCTION(self):
        return

    def __PARAMETERS(self):
        return

    def __VAR_DECL(self):
        return

    def __STATEMENT(self):
        return

    def __RETURN_STMT(self):
        return

    def __FOR_STMT(self):
        return

    def __WHILE_STMT(self):
        return

    def __IF_STMT(self):
        return

    def __BLOCK(self):
        return

    def __EXPR_STMT(self):
        return

    def __PRINT_STMT(self):
        return

    def __EXPRESSION(self):
        return

    def __ASSIGNMENT(self):
        return

    def __LOGIC_OR(self):
        return

    def __LOGIC_AND(self):
        return

    def __EQUALITY(self):
        return

    def __COMPARISON(self):
        return

    def __ADDITION(self):
        return

    def __MULTIPLICATION(self):
        return

    def __UNARY(self):
        return

    def __CALL(self):
        return

    def __ARGUMENTS(self):
        return

    def __PRIMARY(self):
        return

    def __error(self, token: Token, message: str):
        self.onError(token, message)
        raise ParseError(token, message)

    def __consume(self, token_type: TokenType, message: str) -> Optional[Token]:
        if self.__tokenIs(token_type):
            return self.__advance()
        self.__error(self.__peek(), message)

    def __match(self, *args: TokenType) -> bool:
        for tokentype in args:
            if self.__tokenIs(tokentype):
                self.__advance()
                return True
        return False

    def __tokenIs(self, tokentype: TokenType) -> bool:
        return self.__peek().tokenType == tokentype

    def __advance(self) -> Token:
        current = self.__peek()
        if not self.__isAtEnd():
            self.__current += 1
        return current

    def __isAtEnd(self) -> bool:
        return self.__peek().tokenType == TokenType.EOF

    def __peek(self) -> Token:
        return self.__tokens[self.__current]

    def __recoverFromError(self):
        return
