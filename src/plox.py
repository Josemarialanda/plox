import sys
import os
import readline
from parser.parser import Parser
from parser.stmt import Stmt
from typing import Any
from resolver.resolver import Resolver
from runtime.interpreter import Interpreter
from runtime.interpreter import stringify
from scanner.scanner import Scanner
from scanner.token import Token
from scanner.scanError import ScanError
from parser.parseError import ParseError
from resolver.resolveError import ResolveError
from runtime.ploxRuntimeError import PloxRuntimeError
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
            match line:
                case "!exit":
                    print("Bye!")
                    break
                case "!clear":
                    print("\033[H\033[J")
                    continue
                case "!help":
                    print("Type '!exit' to exit the prompt.")
                    print("Type '!clear' to clear the prompt.")
                    continue
                case "!pwd":
                    print(os.getcwd())
                    continue
                case "":
                    continue
            self.source = line
            result = self.run()
            if result is not None:
                prettyResult = stringify(result)
                print(prettyResult)
            self.__hadError = False

    def run(self) -> Any:
        tokens = self.__runScanner(self.source)
        if self.__hadError:
            return
        program = self.__runParser(tokens)
        if self.__hadError:
            return
        self.__runResolver(program)
        return self.__runInterpreter(program)

    def __runScanner(self, source: str) -> list[Token]:
        scanner = Scanner(self.__runtime)
        scanner.run(source)
        if self.__hadError:
            return []
        return scanner.tokens

    def __runParser(self, tokens: list[Token]) -> list[Stmt]:
        parser = Parser(self.__runtime)
        parser.run(tokens)
        if self.__hadError:
            return []
        return parser.program

    def __runResolver(self, program: list[Stmt]):
        resolver = Resolver(self.__interpreter, self.__runtime)
        resolver.run(program)

    def __runInterpreter(self, program: list[Stmt]) -> Any:
        self.__interpreter.run(program)
        return self.__interpreter.result

    def reportError(
        self, error: ScanError | ParseError | ResolveError | PloxRuntimeError
    ):
        if isinstance(error, ScanError):
            print("\nLexical Error:")
            print(f"\t{error.message} at line {error.line}\n")
            self.__hadError = True
        elif isinstance(error, ParseError) or isinstance(error, ResolveError):
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
