from antlr.CompiscriptParser import CompiscriptParser
import uuid
from SymbolTable import AnyType, NumberType, StringType, BoolType, NilType, ObjectType, FunctionType, ClassType
from IntermediateCodeQuadruple import IntermediateCodeQuadruple
from IntermediateCodeTokens import NIL
class IntermediateCodeGenerator:

  def __init__(self, symbolTable, semanticErrors = []) -> None:
    self.symbolTable = symbolTable
    self.semanticErrors = semanticErrors
    self.tempCounter = 0
    self.labelCounter = 0
    self.intermediateCode = IntermediateCodeQuadruple()
    
  def newTemp(self, value):
    """
    Crea un nuevo temporal y lo agrega a la tabla de simbolos
    value: debe ser un valor primitivo o un ObjectType
    """
    tempName = f"t{self.tempCounter}-{uuid.uuid4()}"
    self.tempCounter += 1
    return self.symbolTable.currentScope.addTemporary(tempName, value)
    
  def newLabel(self):
    """
    Crea un nuevo label
    """
    return f"L{self.labelCounter}"
  
  def enterProgram(self, ctx: CompiscriptParser.ProgramContext):
    if len(self.semanticErrors) > 0: return

  def exitProgram(self, ctx: CompiscriptParser.ProgramContext):
    if len(self.semanticErrors) > 0: return

  def enterDeclaration(self, ctx: CompiscriptParser.DeclarationContext):
    if len(self.semanticErrors) > 0: return

  def exitDeclaration(self, ctx: CompiscriptParser.DeclarationContext):
    if len(self.semanticErrors) > 0: return

  def enterClassDecl(self, ctx: CompiscriptParser.ClassDeclContext):
    if len(self.semanticErrors) > 0: return

  def exitClassDecl(self, ctx: CompiscriptParser.ClassDeclContext):
    if len(self.semanticErrors) > 0: return

  def enterFunDecl(self, ctx: CompiscriptParser.FunDeclContext):
    if len(self.semanticErrors) > 0: return

  def exitFunDecl(self, ctx: CompiscriptParser.FunDeclContext):
    if len(self.semanticErrors) > 0: return

  def enterVarDecl(self, ctx: CompiscriptParser.VarDeclContext):
    if len(self.semanticErrors) > 0: return

  def exitVarDecl(self, ctx: CompiscriptParser.VarDeclContext):
    if len(self.semanticErrors) > 0: return

  def enterStatement(self, ctx: CompiscriptParser.StatementContext):
    if len(self.semanticErrors) > 0: return

  def exitStatement(self, ctx: CompiscriptParser.StatementContext):
    if len(self.semanticErrors) > 0: return

  def enterBreakStmt(self, ctx: CompiscriptParser.BreakStmtContext):
    if len(self.semanticErrors) > 0: return

  def exitBreakStmt(self, ctx: CompiscriptParser.BreakStmtContext):
    if len(self.semanticErrors) > 0: return

  def enterContinueStmt(self, ctx: CompiscriptParser.ContinueStmtContext):
    if len(self.semanticErrors) > 0: return

  def exitContinueStmt(self, ctx: CompiscriptParser.ContinueStmtContext):
    if len(self.semanticErrors) > 0: return

  def enterExprStmt(self, ctx: CompiscriptParser.ExprStmtContext):
    if len(self.semanticErrors) > 0: return

  def exitExprStmt(self, ctx: CompiscriptParser.ExprStmtContext):
    if len(self.semanticErrors) > 0: return

  def enterForStmt(self, ctx: CompiscriptParser.ForStmtContext):
    if len(self.semanticErrors) > 0: return

  def exitForStmt(self, ctx: CompiscriptParser.ForStmtContext):
    if len(self.semanticErrors) > 0: return

  def enterIfStmt(self, ctx: CompiscriptParser.IfStmtContext):
    if len(self.semanticErrors) > 0: return

  def exitIfStmt(self, ctx: CompiscriptParser.IfStmtContext):
    if len(self.semanticErrors) > 0: return

  def enterPrintStmt(self, ctx: CompiscriptParser.PrintStmtContext):
    if len(self.semanticErrors) > 0: return

  def exitPrintStmt(self, ctx: CompiscriptParser.PrintStmtContext):
    if len(self.semanticErrors) > 0: return

  def enterReturnStmt(self, ctx: CompiscriptParser.ReturnStmtContext):
    if len(self.semanticErrors) > 0: return

  def exitReturnStmt(self, ctx: CompiscriptParser.ReturnStmtContext):
    if len(self.semanticErrors) > 0: return

  def enterWhileStmt(self, ctx: CompiscriptParser.WhileStmtContext):
    if len(self.semanticErrors) > 0: return

  def exitWhileStmt(self, ctx: CompiscriptParser.WhileStmtContext):
    if len(self.semanticErrors) > 0: return

  def enterBlock(self, ctx: CompiscriptParser.BlockContext):
    if len(self.semanticErrors) > 0: return

  def exitBlock(self, ctx: CompiscriptParser.BlockContext):
    if len(self.semanticErrors) > 0: return

  def enterFunAnon(self, ctx: CompiscriptParser.FunAnonContext):
    if len(self.semanticErrors) > 0: return

  def exitFunAnon(self, ctx: CompiscriptParser.FunAnonContext):
    if len(self.semanticErrors) > 0: return

  def enterExpression(self, ctx: CompiscriptParser.ExpressionContext):
    if len(self.semanticErrors) > 0: return

  def exitExpression(self, ctx: CompiscriptParser.ExpressionContext):
    if len(self.semanticErrors) > 0: return

  def enterAssignment(self, ctx: CompiscriptParser.AssignmentContext):
    if len(self.semanticErrors) > 0: return

  def exitAssignment(self, ctx: CompiscriptParser.AssignmentContext):
    if len(self.semanticErrors) > 0: return

  def enterLogic_or(self, ctx: CompiscriptParser.Logic_orContext):
    if len(self.semanticErrors) > 0: return

  def exitLogic_or(self, ctx: CompiscriptParser.Logic_orContext):
    if len(self.semanticErrors) > 0: return

  def enterLogic_and(self, ctx: CompiscriptParser.Logic_andContext):
    if len(self.semanticErrors) > 0: return

  def exitLogic_and(self, ctx: CompiscriptParser.Logic_andContext):
    if len(self.semanticErrors) > 0: return

  def enterEquality(self, ctx: CompiscriptParser.EqualityContext):
    if len(self.semanticErrors) > 0: return

  def exitEquality(self, ctx: CompiscriptParser.EqualityContext):
    if len(self.semanticErrors) > 0: return

  def enterComparison(self, ctx: CompiscriptParser.ComparisonContext):
    if len(self.semanticErrors) > 0: return

  def exitComparison(self, ctx: CompiscriptParser.ComparisonContext):
    if len(self.semanticErrors) > 0: return

  def enterTerm(self, ctx: CompiscriptParser.TermContext):
    if len(self.semanticErrors) > 0: return

  def exitTerm(self, ctx: CompiscriptParser.TermContext):
    if len(self.semanticErrors) > 0: return

  def enterFactor(self, ctx: CompiscriptParser.FactorContext):
    if len(self.semanticErrors) > 0: return

  def exitFactor(self, ctx: CompiscriptParser.FactorContext):
    if len(self.semanticErrors) > 0: return

  def enterArray(self, ctx: CompiscriptParser.ArrayContext):
    if len(self.semanticErrors) > 0: return

  def exitArray(self, ctx: CompiscriptParser.ArrayContext):
    if len(self.semanticErrors) > 0: return

  def enterInstantiation(self, ctx: CompiscriptParser.InstantiationContext):
    if len(self.semanticErrors) > 0: return

  def exitInstantiation(self, ctx: CompiscriptParser.InstantiationContext):
    if len(self.semanticErrors) > 0: return

  def enterUnary(self, ctx: CompiscriptParser.UnaryContext):
    if len(self.semanticErrors) > 0: return

  def exitUnary(self, ctx: CompiscriptParser.UnaryContext):
    if len(self.semanticErrors) > 0: return

  def enterCall(self, ctx: CompiscriptParser.CallContext):
    if len(self.semanticErrors) > 0: return

  def exitCall(self, ctx: CompiscriptParser.CallContext):
    if len(self.semanticErrors) > 0: return

  def enterPrimary(self, ctx: CompiscriptParser.PrimaryContext):
    if len(self.semanticErrors) > 0: return

  def exitPrimary(self, ctx: CompiscriptParser.PrimaryContext):
    if len(self.semanticErrors) > 0: return
    
    if len(ctx.children):
      # Un solo nodo hijo
      nodeType = ctx.type
      lexeme = ctx.getChild(0).getText()

      if isinstance(nodeType,(NumberType, StringType)):
        
        # Crear un nuevo temporal con valor
        temp = self.newTemp(lexeme)
        # Guardar asignación en CI
        self.intermediateCode.add(result=temp, arg1=lexeme)
        ctx.addr = temp
        
      elif isinstance(nodeType, NilType):
        temp = self.newTemp(NIL)
        self.intermediateCode.add(result=temp, arg1=NIL)
        ctx.addr = temp
      
      elif isinstance(nodeType, (ObjectType, FunctionType, ClassType)):
        ctx.addr = nodeType
        
      
    
    else:
      pass

  def enterFunction(self, ctx: CompiscriptParser.FunctionContext):
    if len(self.semanticErrors) > 0: return

  def exitFunction(self, ctx: CompiscriptParser.FunctionContext):
    if len(self.semanticErrors) > 0: return

  def enterParameters(self, ctx: CompiscriptParser.ParametersContext):
    if len(self.semanticErrors) > 0: return

  def exitParameters(self, ctx: CompiscriptParser.ParametersContext):
    if len(self.semanticErrors) > 0: return

  def enterArguments(self, ctx: CompiscriptParser.ArgumentsContext):
    if len(self.semanticErrors) > 0: return

  def exitArguments(self, ctx: CompiscriptParser.ArgumentsContext):
    if len(self.semanticErrors) > 0: return
