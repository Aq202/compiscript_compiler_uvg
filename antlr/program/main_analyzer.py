import sys
from antlr4 import *
from gen.CompiscriptLexer import CompiscriptLexer
from gen.CompiscriptParser import CompiscriptParser
from gen.CompiscriptListener import CompiscriptListener
from anytree import Node, RenderTree, AsciiStyle
from anytree.exporter import DotExporter

class CompiscriptSemanticChecker(CompiscriptListener):

    def exitFunDecl(self, ctx: CompiscriptParser.ProgramContext):

        for child in ctx.getChildren():
            if not isinstance(child, tree.Tree.TerminalNode):
                print("Nombre de función declarada: ", child.getToken(CompiscriptParser.IDENTIFIER, 0).getText())

        return super().exitProgram(ctx)
def create_tree(node, parser, parent=None):
    if node.getChildCount() == 0:  # Es una hoja
        return Node(node.getText(), parent=parent)
    
    rule_name = parser.ruleNames[node.getRuleIndex()]
    tree_node = Node(rule_name, parent=parent)
    for child in node.getChildren():
        create_tree(child, parser, tree_node)
    return tree_node

def main():
    input_stream = FileStream(sys.argv[1])
    lexer = CompiscriptLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CompiscriptParser(stream)
    tree = parser.program() # program es la regla inicial de gramática
    print(tree.toStringTree(recog=parser))
    

    # Dibujar arbol sintáctico
    root = create_tree(tree, parser)

    for pre, fill, node in RenderTree(root, style=AsciiStyle()):
        print("%s%s" % (pre, node.name))

    # Realizar análisis semantico
    semantic_checker = CompiscriptSemanticChecker()
    walker = ParseTreeWalker()
    walker.walk(semantic_checker, tree)

if __name__ == '__main__':
    main()