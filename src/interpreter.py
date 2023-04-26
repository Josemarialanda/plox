import sys
from scanner.scanner import Scanner

def runFile(path):
  result = []
  with open(path) as file:
    source = file.read()
    scanner = Scanner(source)
    scanner.run()
    if scanner.hasError:
      print("Syntax error(s)")
      for error in scanner.errors:
        print(error)
    else:
      result = scanner.tokens
      
  for token in result:
    print(token)
        
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