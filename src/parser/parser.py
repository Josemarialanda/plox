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

from parser.expr import (
    Assign,
    Binary,
    Call,
    Expr,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    Super,
    This,
    Unary,
    Variable,
)
from parser.parserError import ParseError
from parser.stmt import (
    Block,
    Class,
    Expression,
    Function,
    If,
    Print,
    Return,
    Stmt,
    Var,
    While,
)
from typing import Optional

from scanner.token import Token
from scanner.tokenType import TokenType


class Parser:
    def __init__(self, __tokens: list[Token]):
        self.__tokens = __tokens
        self.__current = 0
        self.__program: list[Stmt] = []
        self.__hadError = False

    @property
    def program(self) -> list[Stmt]:
        return self.__program

    @property
    def hadError(self) -> bool:
        return self.__hadError

    def run(self):
        self.__parse()

    def __parse(self):
        while not self.__isAtEnd():
            if declaration := self.__DECLARATION():
                self.__program.append(declaration)

    def __DECLARATION(self) -> Optional[Stmt]:
        try:
            if self.__match(TokenType.CLASS):
                return self.__CLASS_DECLARATION()
            if self.__match(TokenType.FUN):
                return self.__FUNCTION("function")
            if self.__match(TokenType.VAR):
                return self.__VAR_DECLARATION()
            return self.__STATEMENT()
        except ParseError as error:
            print(error)
            self.__synchronize()
            return None

    def __CLASS_DECLARATION(self) -> Stmt:
        name = self.__consume(TokenType.IDENTIFIER, "Expect class name.")
        superclass = None
        if self.__match(TokenType.LESS):
            self.__consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = Variable(self.__previous())
        self.__consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")
        methods = []
        while not self.__check(TokenType.RIGHT_BRACE) and not self.__isAtEnd():
            methods.append(self.__FUNCTION("method"))
        self.__consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        assert name is not None
        return Class(name=name, superclass=superclass, methods=methods)

    def __FUNCTION(self, kind: str) -> Function:
        name = self.__consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.__consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []
        if not self.__check(TokenType.RIGHT_PAREN):
            parameters.append(
                self.__consume(TokenType.IDENTIFIER, "Expect parameter name.")
            )
            while self.__match(TokenType.COMMA):
                if len(parameters) >= 255:
                    self.__error(self.__peek(), "Cannot have more than 255 parameters.")
                parameters.append(
                    self.__consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )
        self.__consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.__consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.__BLOCK()
        assert name is not None
        return Function(name=name, params=parameters, body=body)

    def __VAR_DECLARATION(self) -> Stmt:
        name = self.__consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.__match(TokenType.EQUAL):
            initializer = self.__EXPRESSION()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        assert name is not None
        return Var(name=name, initializer=initializer)

    def __STATEMENT(self) -> Stmt:
        if self.__match(TokenType.FOR):
            return self.__FOR_STATEMENT()
        if self.__match(TokenType.IF):
            return self.__IF_STATEMENT()
        if self.__match(TokenType.PRINT):
            return self.__PRINT_STATEMENT()
        if self.__match(TokenType.RETURN):
            return self.__RETURN_STATEMENT()
        if self.__match(TokenType.WHILE):
            return self.__WHILE_STATEMENT()
        if self.__match(TokenType.LEFT_BRACE):
            return Block(self.__BLOCK())
        return self.__EXPRESSION_STATEMENT()

    def __BLOCK(self) -> list[Stmt]:
        statements = []
        while not self.__check(TokenType.RIGHT_BRACE) and not self.__isAtEnd():
            statements.append(self.__DECLARATION())
        self.__consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def __FOR_STATEMENT(self) -> Stmt:
        self.__consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        if self.__match(TokenType.SEMICOLON):
            initializer = None
        elif self.__match(TokenType.VAR):
            initializer = self.__VAR_DECLARATION()
        else:
            initializer = self.__EXPRESSION_STATEMENT()
        condition = None
        if not self.__check(TokenType.SEMICOLON):
            condition = self.__EXPRESSION()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
        increment = None
        if not self.__check(TokenType.RIGHT_PAREN):
            increment = self.__EXPRESSION()
        self.__consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        body = self.__STATEMENT()
        if increment:
            body = Block([body, Expression(increment)])
        if condition is None:
            condition = Literal(True)
        body = While(condition, body)
        if initializer is not None:
            body = Block([initializer, body])
        return body

    def __IF_STATEMENT(self) -> Stmt:
        self.__consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: Expr = self.__EXPRESSION()
        self.__consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        then_branch = self.__STATEMENT()
        else_branch = None
        if self.__match(TokenType.ELSE):
            else_branch = self.__STATEMENT()
        return If(condition=condition, then_branch=then_branch, else_branch=else_branch)

    def __PRINT_STATEMENT(self) -> Stmt:
        value = self.__EXPRESSION()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def __RETURN_STATEMENT(self) -> Stmt:
        keyword = self.__previous()
        value = None
        if not self.__check(TokenType.SEMICOLON):
            value = self.__EXPRESSION()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword=keyword, value=value)

    def __WHILE_STATEMENT(self) -> Stmt:
        self.__consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.__EXPRESSION()
        self.__consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.__STATEMENT()
        return While(condition=condition, body=body)

    def __EXPRESSION_STATEMENT(self) -> Stmt:
        expr = self.__EXPRESSION()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Expression(expr)

    def __EXPRESSION(self) -> Expr:
        return self.__ASSIGNMENT()

    def __ASSIGNMENT(self) -> Expr:
        expr = self.__OR()
        if self.__match(TokenType.EQUAL):
            equals = self.__previous()
            value = self.__ASSIGNMENT()
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name=name, value=value)
            elif isinstance(expr, Get):
                return Set(expr.obj, expr.name, value)
            self.__error(equals, "Invalid assignment target.")
        return expr

    def __OR(self) -> Expr:
        expr = self.__AND()
        while self.__match(TokenType.OR):
            operator = self.__previous()
            right = self.__AND()
            expr = Logical(left=expr, operator=operator, right=right)
        return expr

    def __AND(self) -> Expr:
        expr = self.__EQUALITY()
        while self.__match(TokenType.AND):
            operator = self.__previous()
            right = self.__EQUALITY()
            expr = Logical(left=expr, operator=operator, right=right)
        return expr

    def __EQUALITY(self) -> Expr:
        expr = self.__COMPARISON()
        while self.__match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.__previous()
            right = self.__COMPARISON()
            expr = Binary(expr, operator, right)
        return expr

    def __COMPARISON(self) -> Expr:
        expr = self.__ADDITION()
        while self.__match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.__previous()
            right = self.__ADDITION()
            expr = Binary(expr, operator, right)
        return expr

    def __ADDITION(self) -> Expr:
        expr = self.__MULTIPLICATION()
        while self.__match(TokenType.MINUS, TokenType.PLUS):
            operator = self.__previous()
            right = self.__MULTIPLICATION()
            expr = Binary(expr, operator, right)
        return expr

    def __MULTIPLICATION(self) -> Expr:
        expr = self.__UNARY()
        while self.__match(TokenType.SLASH, TokenType.STAR):
            operator = self.__previous()
            right = self.__UNARY()
            expr = Binary(expr, operator, right)
        return expr

    def __UNARY(self) -> Expr:
        if self.__match(TokenType.BANG, TokenType.MINUS):
            operator = self.__previous()
            right = self.__UNARY()
            return Unary(operator, right)
        return self.__CALL()

    def __FINISH_CALL(self, callee: Expr) -> Expr:
        arguments = []
        if not self.__check(TokenType.RIGHT_PAREN):
            arguments.append(self.__EXPRESSION())
            while self.__match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self.__error(self.__peek(), "Cannot have more than 255 arguments.")
                arguments.append(self.__EXPRESSION())
        paren = self.__consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        assert paren is not None
        return Call(callee=callee, paren=paren, arguments=arguments)

    def __CALL(self) -> Expr:
        expr = self.__PRIMARY()
        while True:
            if self.__match(TokenType.LEFT_PAREN):
                expr = self.__FINISH_CALL(expr)
            elif self.__match(TokenType.DOT):
                name = self.__consume(
                    TokenType.IDENTIFIER, "Expect property name after '.'."
                )
                assert name is not None
                expr = Get(expr, name)
            else:
                break
        return expr

    def __PRIMARY(self) -> Expr:
        if self.__match(TokenType.FALSE):
            return Literal(False)
        if self.__match(TokenType.TRUE):
            return Literal(True)
        if self.__match(TokenType.NIL):
            return Literal(None)
        if self.__match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.__previous().literal)
        if self.__match(TokenType.SUPER):
            keyword = self.__previous()
            self.__consume(TokenType.DOT, "Expect '.' after 'super'.")
            method = self.__consume(
                TokenType.IDENTIFIER, "Expect superclass method name."
            )
            assert method is not None
            return Super(keyword, method)
        if self.__match(TokenType.THIS):
            return This(self.__previous())
        if self.__match(TokenType.IDENTIFIER):
            return Variable(self.__previous())
        if self.__match(TokenType.LEFT_PAREN):
            expr = self.__EXPRESSION()
            self.__consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        self.__hadError = True
        raise ParseError(self.__peek(), "Expect expression")

    def __match(self, *args: TokenType) -> bool:
        for tokentype in args:
            if self.__check(tokentype):
                self.__advance()
                return True
        return False

    def __consume(self, token_type: TokenType, message: str):
        if self.__check(token_type):
            return self.__advance()
        self.__error(self.__peek(), message)

    def __check(self, tokentype: TokenType) -> bool:
        if self.__isAtEnd():
            return False
        return self.__peek().tokenType == tokentype

    def __advance(self) -> Token:
        if not self.__isAtEnd():
            self.__current += 1
        return self.__previous()

    def __peek(self) -> Token:
        return self.__tokens[self.__current]

    def __previous(self) -> Token:
        return self.__tokens[self.__current - 1]

    def __isAtEnd(self) -> bool:
        return self.__peek().tokenType == TokenType.EOF

    def __error(self, token: Token, message: str):
        self.__hadError = True
        raise ParseError(token, message)

    def __synchronize(self):
        self.__advance()
        while not self.__isAtEnd():
            if self.__previous().tokenType == TokenType.SEMICOLON:
                return
            if self.__peek().tokenType in [
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ]:
                return
            self.__advance()
