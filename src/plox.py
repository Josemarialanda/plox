import sys
from parser.parser import Parser
from parser.stmt import Stmt
from typing import Any
from resolver.resolver import Resolver
from runtime.interpreter import Interpreter
from scanner.scanner import Scanner
from scanner.token import Token


def runFile(path: str):
    with open(path) as file:
        source = file.read()
        tokens = runScanner(source)
        program = runParser(tokens)
        resolvedProgram = runResolver(program)
        result = runInterpreter(resolvedProgram)
        print(result)
    exit(0)


def runScanner(source: str) -> list[Token]:
    scanner = Scanner(source)
    scanner.run()
    if scanner.hadError:
        exit(65)
    return scanner.tokens


def runParser(tokens: list[Token]) -> list[Stmt]:
    parser = Parser(tokens)
    parser.run()
    if parser.hadError:
        exit(65)
    return parser.program


def runResolver(program: list[Stmt]) -> list[Stmt]:
    resolver = Resolver(program)
    resolver.run()
    if resolver.hadError:
        exit(65)
    return resolver.resolvedProgram


def runInterpreter(program: list[Stmt]) -> Any:
    interpreter = Interpreter(program)
    interpreter.run()
    if interpreter.hadError:
        exit(65)
    return interpreter.result


def runPrompt():
    print("Running prompt")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 1:
        print("Usage: lox [script]")
        exit(64)
    elif len(args) == 1:
        runFile(args[0])
    else:
        runPrompt()
