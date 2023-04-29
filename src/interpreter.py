import sys

from scanner.scanner import Scanner
from scanner.token import Token
from parser.parser import Parser
from parser.stmt import Stmt


def runFile(path: str):
    with open(path) as file:
        source = file.read()
        tokens = runScanner(source)
        program = runParser(tokens)
        # run resolver
        # run evaluator


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
