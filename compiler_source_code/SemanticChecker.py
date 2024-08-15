from antlr4 import *
from antlr.CompiscriptListener import CompiscriptListener
from antlr.CompiscriptParser import CompiscriptParser
from SymbolTable import SymbolTable

class SemanticChecker(CompiscriptListener):    
    def enterBlock(self, ctx: CompiscriptParser.BlockContext):
        
        print("Entrando a nuevo ámbito")
        SymbolTable.createScope()


    def exitBlock(self, ctx: CompiscriptParser.BlockContext):
        
        print("Saliendo de ámbito")
        SymbolTable.dropCurrentScope()


    def enterPrimary(self, ctx: CompiscriptParser.PrimaryContext):
        print("enterPrimary: ", ctx.getText())
        ctx.type = "int"

    def exitCall(self, ctx: CompiscriptParser.CallContext):
        print("exitCall: ", ctx.getText())
        
        for child in ctx.getChildren():
            if not isinstance(child, tree.Tree.TerminalNode):
                print(child.type)