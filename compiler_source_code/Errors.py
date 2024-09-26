from DataType import DataType
class CompilerError(Exception, DataType):
    def __init__(self, message):
        self.message = message

    def equalsType(self, __class__):
        return isinstance(self, __class__)
    
    def strictEqualsType(self, __class__):
        return isinstance(self, __class__)

    def __str__(self):
        return f"CompilerError(message={self.message!r})"

    def __repr__(self):
        return f"CompilerError(message={self.message!r})"
    
    def getType(self):
        return self

class SemanticError(CompilerError):
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        return f"SemanticError(message={self.message!r}, line={self.line}, column={self.column})"
    
    def __repr__(self):
        return f"SemanticError(message={self.message!r}, line={self.line}, column={self.column})"
    

class LexicalError(CompilerError):
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        return f"LexicalError(message={self.message!r}, line={self.line}, column={self.column})"
    
    def __repr__(self):
        return f"LexicalError(message={self.message!r}, line={self.line}, column={self.column})"

class SyntaxError(CompilerError):
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        return f"SyntaxError(message={self.message!r}, line={self.line}, column={self.column})"
    
    def __repr__(self):
        return f"SyntaxError(message={self.message!r}, line={self.line}, column={self.column})"