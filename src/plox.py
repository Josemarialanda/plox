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
from enum import Enum


class RunMode(Enum):
    FILE = 0
    PROMPT = 1


class Plox:
    def __init__(self):
        self.__hadError = False
        self.__runtime = self
        self.__interpreter = Interpreter(self.__runtime)

    def runFile(self, path: str):
        self.__runMode = RunMode.FILE
        with open(path) as file:
            self.source = file.read()
        self.run()
        if self.__hadError:
            sys.exit(65)
        exit(0)

    def runPrompt(self):
        self.__runMode = RunMode.PROMPT
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
        self.runResolver(program)
        return self.runInterpreter(program)

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

    def runResolver(self, program: list[Stmt]):
        resolver = Resolver(self.__interpreter, self.__runtime)
        resolver.run(program)

    def runInterpreter(self, program: list[Stmt]) -> Any:
        self.__interpreter.run(program)
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
            if self.__runMode == RunMode.FILE:
                sys.exit(70)


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
