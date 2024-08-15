class SemanticError(Exception):
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        return f"SemanticError(message={self.message!r}, line={self.line}, column={self.column})"
    
    def __repr__(self):
        return f"SemanticError(message={self.message!r}, line={self.line}, column={self.column})"