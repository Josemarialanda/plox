import sys
from lexer import Lexer

def runFile(path):
  Lexer(path)
  
def runPrompt():
  print("Running prompt")

if __name__ == "__main__":
  args = sys.argv[1:]
  if (len(args) > 1):
    print("Usage: lox [script]")
    exit(64)
  elif (len(args) == 1):
    runFile(args[0])
  else:
    runPrompt()