class ResolveError(Exception):
    def __init__(self, line, message):
        self.line = line
        self.message = message
