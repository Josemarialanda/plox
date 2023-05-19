import sys
import readline
from parser.parser import Parser
from parser.stmt import Stmt
from typing import Any
from resolver.resolver import Resolver
from runtime.interpreter import Interpreter
from scanner.scanner import Scanner
from scanner.token import Token
from scanner.scanError import ScanError
from parser.parseError import ParseError
from runtime.ploxRuntimeError import PloxRuntimeError
from utils import stringify


class Plox:
    def __init__(self):
        self.__hadError = False
        self.__hadRuntimeError = False
        self.__runtime = self
        self.__interpreter = Interpreter(self.__runtime)

    def runFile(self, path: str):
        with open(path) as file:
            self.source = file.read()
        self.run()
        if self.__hadError:
            sys.exit(65)
        if self.__hadRuntimeError:
            sys.exit(70)
        exit(0)

    def runPrompt(self):
        while True:
            line = input("plox > ")
            if line in ["exit"]:
                break
            self.source = line
            result = self.run()
            if result is not None:
                prettyResult = stringify(result)
                print(prettyResult)
            self.__hadError = False

    def run(self) -> Any:
        tokens = self.runScanner(self.source)
        if self.__hadError:
            return
        program = self.runParser(tokens)
        if self.__hadError:
            return
        # resolvedProgram = self.runResolver(program)
        # if self.__hadError:
        #     return
        result = self.runInterpreter(program)
        if self.__hadRuntimeError:
            return
        return result

    def runScanner(self, source: str) -> list[Token]:
        scanner = Scanner(self.__runtime)
        scanner.run(source)
        if self.__hadError:
            return []
        return scanner.tokens

    def runParser(self, tokens: list[Token]) -> list[Stmt]:
        parser = Parser(self.__runtime)
        parser.run(tokens)
        if self.__hadError:
            return []
        return parser.program

    def runResolver(self, program: list[Stmt]) -> list[Stmt]:
        resolver = Resolver(self.__runtime)
        resolver.run(program)
        if self.__hadError:
            return []
        return resolver.resolvedProgram

    def runInterpreter(self, program: list[Stmt]) -> Any:
        self.__interpreter.run(program)
        if self.__hadRuntimeError | self.__hadError:
            return
        return self.__interpreter.result

    def reportError(self, error: ScanError | ParseError | PloxRuntimeError):
        if isinstance(error, ScanError):
            print("\nLexical Error:")
            print(f"\t{error.message} at line {error.line}\n")
            self.__hadError = True
        elif isinstance(error, ParseError):
            print("\nSyntax Error")
            print(f"\t{error.message} at line {error.line}\n")
            self.__hadError = True
        else:
            print("\nRuntime Error")
            print(f"\t{error.message} at line {error.token.line}\n")
            self.__hadRuntimeError = True


if __name__ == "__main__":
    lox = Plox()
    args = sys.argv[1:]
    if len(args) > 1:
        print("Usage: lox [script]")
        exit(64)
    elif len(args) == 1:
        lox.runFile(args[0])
    else:
        lox.runPrompt()
