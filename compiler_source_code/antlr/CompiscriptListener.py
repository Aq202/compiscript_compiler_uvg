# Generated from Compiscript.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .CompiscriptParser import CompiscriptParser
else:
    from CompiscriptParser import CompiscriptParser

# This class defines a complete listener for a parse tree produced by CompiscriptParser.
class CompiscriptListener(ParseTreeListener):

    # Enter a parse tree produced by CompiscriptParser#program.
    def enterProgram(self, ctx:CompiscriptParser.ProgramContext):
        print("enter program")

    # Exit a parse tree produced by CompiscriptParser#program.
    def exitProgram(self, ctx:CompiscriptParser.ProgramContext):
        print("exit program")

    # Enter a parse tree produced by CompiscriptParser#declaration.
    def enterDeclaration(self, ctx:CompiscriptParser.DeclarationContext):
        print("enter declaration")

    # Exit a parse tree produced by CompiscriptParser#declaration.
    def exitDeclaration(self, ctx:CompiscriptParser.DeclarationContext):
        print("exit declaration")

    # Enter a parse tree produced by CompiscriptParser#classDecl.
    def enterClassDecl(self, ctx:CompiscriptParser.ClassDeclContext):
        print("enter class")

    # Exit a parse tree produced by CompiscriptParser#classDecl.
    def exitClassDecl(self, ctx:CompiscriptParser.ClassDeclContext):
        print("exit class decl")

    # Enter a parse tree produced by CompiscriptParser#funDecl.
    def enterFunDecl(self, ctx:CompiscriptParser.FunDeclContext):
        print("enter funDecl")

    # Exit a parse tree produced by CompiscriptParser#funDecl.
    def exitFunDecl(self, ctx:CompiscriptParser.FunDeclContext):
        print("exit funDecl")

    # Enter a parse tree produced by CompiscriptParser#varDecl.
    def enterVarDecl(self, ctx:CompiscriptParser.VarDeclContext):
        print("enter varDecl")

    # Exit a parse tree produced by CompiscriptParser#varDecl.
    def exitVarDecl(self, ctx:CompiscriptParser.VarDeclContext):
        print("exit varDecl")

    # Enter a parse tree produced by CompiscriptParser#statement.
    def enterStatement(self, ctx:CompiscriptParser.StatementContext):
        print("enter statement")

    # Exit a parse tree produced by CompiscriptParser#statement.
    def exitStatement(self, ctx:CompiscriptParser.StatementContext):
        print("exit statement")

    # Enter a parse tree produced by CompiscriptParser#exprStmt.
    def enterExprStmt(self, ctx:CompiscriptParser.ExprStmtContext):
        print("enter exprStmt")

    # Exit a parse tree produced by CompiscriptParser#exprStmt.
    def exitExprStmt(self, ctx:CompiscriptParser.ExprStmtContext):
        print("exit exprStmt")

    # Enter a parse tree produced by CompiscriptParser#forStmt.
    def enterForStmt(self, ctx:CompiscriptParser.ForStmtContext):
        print("enter forStmt")

    # Exit a parse tree produced by CompiscriptParser#forStmt.
    def exitForStmt(self, ctx:CompiscriptParser.ForStmtContext):
        print("exit forStmt")

    # Enter a parse tree produced by CompiscriptParser#ifStmt.
    def enterIfStmt(self, ctx:CompiscriptParser.IfStmtContext):
        print("enter ifStmt")

    # Exit a parse tree produced by CompiscriptParser#ifStmt.
    def exitIfStmt(self, ctx:CompiscriptParser.IfStmtContext):
        print("exit ifStmt")

    # Enter a parse tree produced by CompiscriptParser#printStmt.
    def enterPrintStmt(self, ctx:CompiscriptParser.PrintStmtContext):
        print("enter printStmt")

    # Exit a parse tree produced by CompiscriptParser#printStmt.
    def exitPrintStmt(self, ctx:CompiscriptParser.PrintStmtContext):
        print("exit printStmt")

    # Enter a parse tree produced by CompiscriptParser#returnStmt.
    def enterReturnStmt(self, ctx:CompiscriptParser.ReturnStmtContext):
        print("enter returnStmt")

    # Exit a parse tree produced by CompiscriptParser#returnStmt.
    def exitReturnStmt(self, ctx:CompiscriptParser.ReturnStmtContext):
        print("exit returnStmt")

    # Enter a parse tree produced by CompiscriptParser#whileStmt.
    def enterWhileStmt(self, ctx:CompiscriptParser.WhileStmtContext):
        print("enter whileStmt")

    # Exit a parse tree produced by CompiscriptParser#whileStmt.
    def exitWhileStmt(self, ctx:CompiscriptParser.WhileStmtContext):
        print("exit whileStmt")

    # Enter a parse tree produced by CompiscriptParser#block.
    def enterBlock(self, ctx:CompiscriptParser.BlockContext):
        print("enter block")

    # Exit a parse tree produced by CompiscriptParser#block.
    def exitBlock(self, ctx:CompiscriptParser.BlockContext):
        print("exit block")

    # Enter a parse tree produced by CompiscriptParser#expression.
    def enterExpression(self, ctx:CompiscriptParser.ExpressionContext):
        print("enter expression")

    # Exit a parse tree produced by CompiscriptParser#expression.
    def exitExpression(self, ctx:CompiscriptParser.ExpressionContext):
        print("exit expression")

    # Enter a parse tree produced by CompiscriptParser#assignment.
    def enterAssignment(self, ctx:CompiscriptParser.AssignmentContext):
        print("enter assignment")

    # Exit a parse tree produced by CompiscriptParser#assignment.
    def exitAssignment(self, ctx:CompiscriptParser.AssignmentContext):
        print("exit assignment")

    # Enter a parse tree produced by CompiscriptParser#logic_or.
    def enterLogic_or(self, ctx:CompiscriptParser.Logic_orContext):
        print("enter logic_or")

    # Exit a parse tree produced by CompiscriptParser#logic_or.
    def exitLogic_or(self, ctx:CompiscriptParser.Logic_orContext):
        print("exit logic_or")

    # Enter a parse tree produced by CompiscriptParser#logic_and.
    def enterLogic_and(self, ctx:CompiscriptParser.Logic_andContext):
        print("enter logic_and")

    # Exit a parse tree produced by CompiscriptParser#logic_and.
    def exitLogic_and(self, ctx:CompiscriptParser.Logic_andContext):
        print("exit logic_and")

    # Enter a parse tree produced by CompiscriptParser#equality.
    def enterEquality(self, ctx:CompiscriptParser.EqualityContext):
        print("enter equality")

    # Exit a parse tree produced by CompiscriptParser#equality.
    def exitEquality(self, ctx:CompiscriptParser.EqualityContext):
        print("exit equality")

    # Enter a parse tree produced by CompiscriptParser#comparison.
    def enterComparison(self, ctx:CompiscriptParser.ComparisonContext):
        print("enter comparison")

    # Exit a parse tree produced by CompiscriptParser#comparison.
    def exitComparison(self, ctx:CompiscriptParser.ComparisonContext):
        print("exit comparison")

    # Enter a parse tree produced by CompiscriptParser#term.
    def enterTerm(self, ctx:CompiscriptParser.TermContext):
        print("enter term")

    # Exit a parse tree produced by CompiscriptParser#term.
    def exitTerm(self, ctx:CompiscriptParser.TermContext):
        print("exit term")

    # Enter a parse tree produced by CompiscriptParser#factor.
    def enterFactor(self, ctx:CompiscriptParser.FactorContext):
        print("enter factor")

    # Exit a parse tree produced by CompiscriptParser#factor.
    def exitFactor(self, ctx:CompiscriptParser.FactorContext):
        print("exit factor")

    # Enter a parse tree produced by CompiscriptParser#unary.
    def enterUnary(self, ctx:CompiscriptParser.UnaryContext):
        print("enter unary")

    # Exit a parse tree produced by CompiscriptParser#unary.
    def exitUnary(self, ctx:CompiscriptParser.UnaryContext):
        print("exit unary")

    # Enter a parse tree produced by CompiscriptParser#call.
    def enterCall(self, ctx:CompiscriptParser.CallContext):
        print("enter call")

    # Exit a parse tree produced by CompiscriptParser#call.
    def exitCall(self, ctx:CompiscriptParser.CallContext):
        print("exit call")

    # Enter a parse tree produced by CompiscriptParser#primary.
    def enterPrimary(self, ctx:CompiscriptParser.PrimaryContext):
        print("enter primary")

    # Exit a parse tree produced by CompiscriptParser#primary.
    def exitPrimary(self, ctx:CompiscriptParser.PrimaryContext):
        print("exit primary")

    # Enter a parse tree produced by CompiscriptParser#function.
    def enterFunction(self, ctx:CompiscriptParser.FunctionContext):
        print("enter function")

    # Exit a parse tree produced by CompiscriptParser#function.
    def exitFunction(self, ctx:CompiscriptParser.FunctionContext):
        print("exit function")

    # Enter a parse tree produced by CompiscriptParser#parameters.
    def enterParameters(self, ctx:CompiscriptParser.ParametersContext):
        print("enter parameters")

    # Exit a parse tree produced by CompiscriptParser#parameters.
    def exitParameters(self, ctx:CompiscriptParser.ParametersContext):
        print("exit parameters")

    # Enter a parse tree produced by CompiscriptParser#arguments.
    def enterArguments(self, ctx:CompiscriptParser.ArgumentsContext):
        print("enter arguments")

    # Exit a parse tree produced by CompiscriptParser#arguments.
    def exitArguments(self, ctx:CompiscriptParser.ArgumentsContext):
        print("exit arguments")


del CompiscriptParser