from antlr4.error.ErrorListener import ErrorListener
from Errors import LexicalError, SyntaxError

class LexerErrorListener(ErrorListener):
  def __init__(self):
    super(LexerErrorListener, self).__init__()
    self.errors = []

  def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
    error = LexicalError(message=msg, line=line, column=column)
    self.errors.append(error)

class ParserErrorListener(ErrorListener):
  def __init__(self):
    super(ParserErrorListener, self).__init__()
    self.errors = []

  def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
    error = SyntaxError(message=msg, line=line, column=column)
    self.errors.append(error) 