import sys
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

class Plox:
    def __init__(self):
        self.__hadError = False
        self.__hadRuntimeError = False
    

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
            self.run()
            self.__hadError = False
            

    def run(self):
        tokens = self.runScanner()
        if self.__hadError: return
        program = self.runParser(tokens)
        if self.__hadError: return
        resolvedProgram = self.runResolver(program)
        if self.__hadError: return
        result = self.runInterpreter(resolvedProgram)
        if self.__hadRuntimeError:return
        prettyResult = self.__stringify(result)
        print(prettyResult)


    def runScanner(self) -> list[Token]:
        scanner = Scanner(self)
        scanner.run()
        if self.__hadError: 
            return []
        return scanner.tokens


    def runParser(self, tokens: list[Token]) -> list[Stmt]:
        parser = Parser(tokens, self)
        parser.run()
        if self.__hadError: 
            return []
        return parser.program


    def runResolver(self, program: list[Stmt]) -> list[Stmt]:
        resolver = Resolver(program, self)
        resolver.run()
        if self.__hadError: 
            return []
        return resolver.resolvedProgram


    def runInterpreter(self, program: list[Stmt]) -> Any:
        interpreter = Interpreter(program, self)
        interpreter.run()
        if self.__hadRuntimeError | self.__hadError: 
            return
        return interpreter.result


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
                error.throwRuntimeError(f"\t{error.message} at line {error.token.line}\n")
                self.__hadRuntimeError = True

    def __stringify(self, obj: Any) -> str:
        if obj is None:
            return "nil"
        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        return str(obj)        

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
