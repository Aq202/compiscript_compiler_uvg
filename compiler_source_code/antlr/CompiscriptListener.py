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
        print("Enter program")

    # Exit a parse tree produced by CompiscriptParser#program.
    def exitProgram(self, ctx:CompiscriptParser.ProgramContext):
        print("Exit program")


    # Enter a parse tree produced by CompiscriptParser#declaration.
    def enterDeclaration(self, ctx:CompiscriptParser.DeclarationContext):
        print("Enter declaration")

    # Exit a parse tree produced by CompiscriptParser#declaration.
    def exitDeclaration(self, ctx:CompiscriptParser.DeclarationContext):
        print("Exit declaration")


    # Enter a parse tree produced by CompiscriptParser#classDecl.
    def enterClassDecl(self, ctx:CompiscriptParser.ClassDeclContext):
        print("Enter classDecl")

    # Exit a parse tree produced by CompiscriptParser#classDecl.
    def exitClassDecl(self, ctx:CompiscriptParser.ClassDeclContext):
        print("Exit classDecl")


    # Enter a parse tree produced by CompiscriptParser#funDecl.
    def enterFunDecl(self, ctx:CompiscriptParser.FunDeclContext):
        print("Enter funDecl")

    # Exit a parse tree produced by CompiscriptParser#funDecl.
    def exitFunDecl(self, ctx:CompiscriptParser.FunDeclContext):
        print("Exit funDecl")


    # Enter a parse tree produced by CompiscriptParser#varDecl.
    def enterVarDecl(self, ctx:CompiscriptParser.VarDeclContext):
        print("Enter varDecl")

    # Exit a parse tree produced by CompiscriptParser#varDecl.
    def exitVarDecl(self, ctx:CompiscriptParser.VarDeclContext):
        print("Exit varDecl")


    # Enter a parse tree produced by CompiscriptParser#statement.
    def enterStatement(self, ctx:CompiscriptParser.StatementContext):
        print("Enter statement")

    # Exit a parse tree produced by CompiscriptParser#statement.
    def exitStatement(self, ctx:CompiscriptParser.StatementContext):
        print("Exit statement")


    # Enter a parse tree produced by CompiscriptParser#exprStmt.
    def enterExprStmt(self, ctx:CompiscriptParser.ExprStmtContext):
        print("Enter exprStmt")

    # Exit a parse tree produced by CompiscriptParser#exprStmt.
    def exitExprStmt(self, ctx:CompiscriptParser.ExprStmtContext):
        print("Exit exprStmt")


    # Enter a parse tree produced by CompiscriptParser#forStmt.
    def enterForStmt(self, ctx:CompiscriptParser.ForStmtContext):
        print("Enter forStmt")

    # Exit a parse tree produced by CompiscriptParser#forStmt.
    def exitForStmt(self, ctx:CompiscriptParser.ForStmtContext):
        print("Exit forStmt")


    # Enter a parse tree produced by CompiscriptParser#ifStmt.
    def enterIfStmt(self, ctx:CompiscriptParser.IfStmtContext):
        print("Enter ifStmt")

    # Exit a parse tree produced by CompiscriptParser#ifStmt.
    def exitIfStmt(self, ctx:CompiscriptParser.IfStmtContext):
        print("Exit ifStmt")


    # Enter a parse tree produced by CompiscriptParser#printStmt.
    def enterPrintStmt(self, ctx:CompiscriptParser.PrintStmtContext):
        print("Enter printStmt")

    # Exit a parse tree produced by CompiscriptParser#printStmt.
    def exitPrintStmt(self, ctx:CompiscriptParser.PrintStmtContext):
        print("Exit printStmt")


    # Enter a parse tree produced by CompiscriptParser#returnStmt.
    def enterReturnStmt(self, ctx:CompiscriptParser.ReturnStmtContext):
        print("Enter returnStmt")

    # Exit a parse tree produced by CompiscriptParser#returnStmt.
    def exitReturnStmt(self, ctx:CompiscriptParser.ReturnStmtContext):
        print("Exit returnStmt")


    # Enter a parse tree produced by CompiscriptParser#whileStmt.
    def enterWhileStmt(self, ctx:CompiscriptParser.WhileStmtContext):
        print("Enter whileStmt")

    # Exit a parse tree produced by CompiscriptParser#whileStmt.
    def exitWhileStmt(self, ctx:CompiscriptParser.WhileStmtContext):
        print("Exit whileStmt")


    # Enter a parse tree produced by CompiscriptParser#block.
    def enterBlock(self, ctx:CompiscriptParser.BlockContext):
        print("Enter block")

    # Exit a parse tree produced by CompiscriptParser#block.
    def exitBlock(self, ctx:CompiscriptParser.BlockContext):
        print("Exit block")


    # Enter a parse tree produced by CompiscriptParser#funAnon.
    def enterFunAnon(self, ctx:CompiscriptParser.FunAnonContext):
        print("Enter funAnon")

    # Exit a parse tree produced by CompiscriptParser#funAnon.
    def exitFunAnon(self, ctx:CompiscriptParser.FunAnonContext):
        print("Exit funAnon")


    # Enter a parse tree produced by CompiscriptParser#expression.
    def enterExpression(self, ctx:CompiscriptParser.ExpressionContext):
        print("Enter expression")

    # Exit a parse tree produced by CompiscriptParser#expression.
    def exitExpression(self, ctx:CompiscriptParser.ExpressionContext):
        print("Exit expression")


    # Enter a parse tree produced by CompiscriptParser#assignment.
    def enterAssignment(self, ctx:CompiscriptParser.AssignmentContext):
        print("Enter assignment")

    # Exit a parse tree produced by CompiscriptParser#assignment.
    def exitAssignment(self, ctx:CompiscriptParser.AssignmentContext):
        print("Exit assignment")


    # Enter a parse tree produced by CompiscriptParser#logic_or.
    def enterLogic_or(self, ctx:CompiscriptParser.Logic_orContext):
        print("Enter logic_or")

    # Exit a parse tree produced by CompiscriptParser#logic_or.
    def exitLogic_or(self, ctx:CompiscriptParser.Logic_orContext):
        print("Exit logic_or")


    # Enter a parse tree produced by CompiscriptParser#logic_and.
    def enterLogic_and(self, ctx:CompiscriptParser.Logic_andContext):
        print("Enter logic_and")

    # Exit a parse tree produced by CompiscriptParser#logic_and.
    def exitLogic_and(self, ctx:CompiscriptParser.Logic_andContext):
        print("Exit logic_and")


    # Enter a parse tree produced by CompiscriptParser#equality.
    def enterEquality(self, ctx:CompiscriptParser.EqualityContext):
        print("Enter equality")

    # Exit a parse tree produced by CompiscriptParser#equality.
    def exitEquality(self, ctx:CompiscriptParser.EqualityContext):
        print("Exit equality")


    # Enter a parse tree produced by CompiscriptParser#comparison.
    def enterComparison(self, ctx:CompiscriptParser.ComparisonContext):
        print("Enter comparison")

    # Exit a parse tree produced by CompiscriptParser#comparison.
    def exitComparison(self, ctx:CompiscriptParser.ComparisonContext):
        print("Exit comparison")


    # Enter a parse tree produced by CompiscriptParser#term.
    def enterTerm(self, ctx:CompiscriptParser.TermContext):
        print("Enter term")

    # Exit a parse tree produced by CompiscriptParser#term.
    def exitTerm(self, ctx:CompiscriptParser.TermContext):
        print("Exit term")


    # Enter a parse tree produced by CompiscriptParser#factor.
    def enterFactor(self, ctx:CompiscriptParser.FactorContext):
        print("Enter factor")

    # Exit a parse tree produced by CompiscriptParser#factor.
    def exitFactor(self, ctx:CompiscriptParser.FactorContext):
        print("Exit factor")


    # Enter a parse tree produced by CompiscriptParser#array.
    def enterArray(self, ctx:CompiscriptParser.ArrayContext):
        print("Enter array")

    # Exit a parse tree produced by CompiscriptParser#array.
    def exitArray(self, ctx:CompiscriptParser.ArrayContext):
        print("Exit array")


    # Enter a parse tree produced by CompiscriptParser#instantiation.
    def enterInstantiation(self, ctx:CompiscriptParser.InstantiationContext):
        print("Enter instantiation")

    # Exit a parse tree produced by CompiscriptParser#instantiation.
    def exitInstantiation(self, ctx:CompiscriptParser.InstantiationContext):
        print("Exit instantiation")


    # Enter a parse tree produced by CompiscriptParser#unary.
    def enterUnary(self, ctx:CompiscriptParser.UnaryContext):
        print("Enter unary")

    # Exit a parse tree produced by CompiscriptParser#unary.
    def exitUnary(self, ctx:CompiscriptParser.UnaryContext):
        print("Exit unary")


    # Enter a parse tree produced by CompiscriptParser#call.
    def enterCall(self, ctx:CompiscriptParser.CallContext):
        print("Enter call")

    # Exit a parse tree produced by CompiscriptParser#call.
    def exitCall(self, ctx:CompiscriptParser.CallContext):
        print("Exit call")

    # Enter a parse tree produced by CompiscriptParser#primary.
    def enterPrimary(self, ctx:CompiscriptParser.PrimaryContext):
        print("Enter primary")

    # Exit a parse tree produced by CompiscriptParser#primary.
    def exitPrimary(self, ctx:CompiscriptParser.PrimaryContext):
        print("Exit primary")


    # Enter a parse tree produced by CompiscriptParser#function.
    def enterFunction(self, ctx:CompiscriptParser.FunctionContext):
        print("Enter function")

    # Exit a parse tree produced by CompiscriptParser#function.
    def exitFunction(self, ctx:CompiscriptParser.FunctionContext):
        print("Exit function")


    # Enter a parse tree produced by CompiscriptParser#parameters.
    def enterParameters(self, ctx:CompiscriptParser.ParametersContext):
        print("Enter parameters")

    # Exit a parse tree produced by CompiscriptParser#parameters.
    def exitParameters(self, ctx:CompiscriptParser.ParametersContext):
        print("Exit parameters")


    # Enter a parse tree produced by CompiscriptParser#arguments.
    def enterArguments(self, ctx:CompiscriptParser.ArgumentsContext):
        print("Enter arguments")

    # Exit a parse tree produced by CompiscriptParser#arguments.
    def exitArguments(self, ctx:CompiscriptParser.ArgumentsContext):
        print("Exit arguments")



del CompiscriptParser