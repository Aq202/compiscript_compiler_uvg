from antlr4 import *
from antlr.CompiscriptLexer import CompiscriptLexer
from antlr.CompiscriptParser import CompiscriptParser
from anytree import Node, RenderTree, AsciiStyle
from SemanticChecker import SemanticChecker
from ErrorListener import LexerErrorListener, ParserErrorListener
from AssemblyGenerator import AssemblyGenerator
from utils.copyToClipboard import copyToClipboard

def create_tree(node, parser, parent=None):
    if node.getChildCount() == 0:  # Es una hoja
        return Node(node.getText(), parent=parent)
    
    rule_name = parser.ruleNames[node.getRuleIndex()]
    tree_node = Node(rule_name, parent=parent)
    for child in node.getChildren():
        create_tree(child, parser, tree_node)
    return tree_node

def main():
    #input_stream = FileStream(sys.argv[1])
    input_stream = FileStream("D:\diego\OneDrive - UVG\Documentos Universidad\Semestre 8\compiladores\proyecto\desarrollo\compiler_source_code\prueba.txt", encoding='utf-8')
    lexer = CompiscriptLexer(input_stream)
    
    lexerErrorListener = LexerErrorListener()
    lexer.removeErrorListeners()
    lexer.addErrorListener(lexerErrorListener)
    

    stream = CommonTokenStream(lexer)
    parser = CompiscriptParser(stream)

    parserErrorListener = ParserErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(parserErrorListener)

    tree = parser.program() # program es la regla inicial de gramática
    
    # Dibujar arbol sintáctico
    root = create_tree(tree, parser)

    for pre, fill, node in RenderTree(root, style=AsciiStyle()):
        print("%s%s" % (pre, node.name))

    # Realizar análisis semantico
    semantic_checker = SemanticChecker(preventCodeGeneration=len(lexerErrorListener.errors) + len(parserErrorListener.errors) > 0)
    walker = ParseTreeWalker()
    walker.walk(semantic_checker, tree)

    # Imprimir errores
    errors = lexerErrorListener.errors + parserErrorListener.errors + semantic_checker.errors
    
    if len(errors) > 0:
        print("\nErrores en el programa:")
        for error in errors:
            print(error)
    else:
        code = semantic_checker.getProgramCode()
        print("\n\nCódigo intermedio:\n", "\n".join([str(line) for line in code]), sep="")
        
        print("\n\nIniciando traducción...")
        assemblyGenerator = AssemblyGenerator(code)
        stringCode = "\n".join(assemblyGenerator.getCode())
        
        copyToClipboard(stringCode)
        
        print("Código ensamblador copiado al portapapeles")

if __name__ == '__main__':
    main()