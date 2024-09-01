from antlr4 import *
from antlr.CompiscriptLexer import CompiscriptLexer
from antlr.CompiscriptParser import CompiscriptParser
from SemanticChecker import SemanticChecker
from ErrorListener import LexerErrorListener, ParserErrorListener

def executeSemanticAnalyzer(filePath):
  """
  Ejecuta el análisis léxico, sintáctico y semántico de un código fuente.
  @param filePath: str - Ruta del archivo a analizar.
  @return has_errors, errors: bool, list - Indica si hubo errores y lista de errores.
  """

  input_stream = FileStream(filePath)
  lexer = CompiscriptLexer(input_stream)
  
  # Capturar errores léxicos
  lexerErrorListener = LexerErrorListener()
  lexer.removeErrorListeners()
  lexer.addErrorListener(lexerErrorListener)
  

  stream = CommonTokenStream(lexer)
  parser = CompiscriptParser(stream)

  # Capturar errores sintácticos
  parserErrorListener = ParserErrorListener()
  parser.removeErrorListeners()
  parser.addErrorListener(parserErrorListener)

  tree = parser.program() # program es la regla inicial de gramática

  # Realizar análisis semantico
  semantic_checker = SemanticChecker()
  walker = ParseTreeWalker()
  walker.walk(semantic_checker, tree)

  # retornar errores
  errors = lexerErrorListener.errors + parserErrorListener.errors + semantic_checker.errors
  
  return len(errors) > 0, errors