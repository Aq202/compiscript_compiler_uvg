from antlr4 import *
from antlr.CompiscriptLexer import CompiscriptLexer
from antlr.CompiscriptParser import CompiscriptParser
from SemanticChecker import SemanticChecker
from ErrorListener import LexerErrorListener, ParserErrorListener
from AssemblyGenerator import AssemblyGenerator

def executeCompilation(filePath):
  """
  Ejecuta el análisis léxico, sintáctico y semántico de un código fuente, posteriormente genera
  el código intermedio y lo traduce a código ensamblador.
  @param filePath: str - Ruta del archivo a analizar.
  @return has_errors, errors, assembly_code: bool, list, str - Indica si hubo errores,
  lista de errores y código ensamblador (str list).
  """
  try:
    input_stream = FileStream(filePath, encoding='utf-8')
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
    
    if len(errors) > 0:
      return True, errors, None
    else:
      # Realizar traducción a código ensamblador
      intermediateCode = semantic_checker.getProgramCode()
      assemblyGenerator = AssemblyGenerator(intermediateCode)
      return False, [], assemblyGenerator.getCode()

  except Exception as e:
    return True, [str(e)], None