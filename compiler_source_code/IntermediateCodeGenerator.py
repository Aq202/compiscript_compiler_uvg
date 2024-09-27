from antlr.CompiscriptParser import CompiscriptParser
import uuid
from compoundTypes import ObjectType, FunctionType, ClassType
from primitiveTypes import NumberType, StringType, NilType
from IntermediateCodeQuadruple import IntermediateCodeQuadruple
from consts import MEM_ADDR_SIZE
from Value import Value


class IntermediateCodeGenerator:

  def __init__(self, symbolTable, semanticErrors = [], stopGeneration=False) -> None:
    self.symbolTable = symbolTable
    self.semanticErrors = semanticErrors
    self.tempCounter = 0
    self.labelCounter = 0
    self.intermediateCode = IntermediateCodeQuadruple()
    self.stopGeneration = stopGeneration
  
  def continueCodeGeneration(self):
    return not self.stopGeneration and len(self.semanticErrors) == 0 
    
  def newTemp(self):
    """
    Crea un nuevo temporal y lo agrega a la tabla de simbolos
    value: debe ser un valor primitivo o un ObjectType
    """
    tempName = f"t{self.tempCounter}-{uuid.uuid4()}"
    self.tempCounter += 1
    temp = self.symbolTable.currentScope.addTemporary(tempName)
    
    # Asignar un offset al temporal
    scope = self.symbolTable.currentScope
    temp.assignOffset(scope.offset, MEM_ADDR_SIZE)
    # Correr offset para siguiente variable
    scope.setOffset(scope.offset + MEM_ADDR_SIZE)
    
    return temp
    
  def newLabel(self):
    """
    Crea un nuevo label
    """
    return f"L{self.labelCounter}"
  
  def enterProgram(self, ctx: CompiscriptParser.ProgramContext):
    if not self.continueCodeGeneration(): return

  def exitProgram(self, ctx: CompiscriptParser.ProgramContext):
    if not self.continueCodeGeneration(): return
    
    print("\nCódigo intermedio:\n",self.intermediateCode)
    

  def enterDeclaration(self, ctx: CompiscriptParser.DeclarationContext):
    if not self.continueCodeGeneration(): return

  def exitDeclaration(self, ctx: CompiscriptParser.DeclarationContext):
    if not self.continueCodeGeneration(): return

  def enterClassDecl(self, ctx: CompiscriptParser.ClassDeclContext):
    if not self.continueCodeGeneration(): return

  def exitClassDecl(self, ctx: CompiscriptParser.ClassDeclContext):
    if not self.continueCodeGeneration(): return

  def enterFunDecl(self, ctx: CompiscriptParser.FunDeclContext):
    if not self.continueCodeGeneration(): return

  def exitFunDecl(self, ctx: CompiscriptParser.FunDeclContext):
    if not self.continueCodeGeneration(): return

  def enterVarDecl(self, ctx: CompiscriptParser.VarDeclContext):
    if not self.continueCodeGeneration(): return

  def exitVarDecl(self, ctx: CompiscriptParser.VarDeclContext, objectDef: ObjectType):
    if not self.continueCodeGeneration(): return
    
    expressionNode = ctx.expression()
    
    # Asignar un offset a la variable
    scope = self.symbolTable.currentScope
    objectDef.assignOffset(scope.offset, MEM_ADDR_SIZE)
    
    scope.setOffset(scope.offset + MEM_ADDR_SIZE) # Correr offset para siguiente variable
    
    if expressionNode is None:
      # Asignar NIL
      self.intermediateCode.add(result=objectDef, arg1=Value(None, NilType()))
    
    else:
      expressionAddr = expressionNode.addr
      self.intermediateCode.add(result=objectDef, arg1=expressionAddr)
    
    ctx.addr = objectDef
      


  def enterStatement(self, ctx: CompiscriptParser.StatementContext):
    if not self.continueCodeGeneration(): return

  def exitStatement(self, ctx: CompiscriptParser.StatementContext):
    if not self.continueCodeGeneration(): return

  def enterBreakStmt(self, ctx: CompiscriptParser.BreakStmtContext):
    if not self.continueCodeGeneration(): return

  def exitBreakStmt(self, ctx: CompiscriptParser.BreakStmtContext):
    if not self.continueCodeGeneration(): return

  def enterContinueStmt(self, ctx: CompiscriptParser.ContinueStmtContext):
    if not self.continueCodeGeneration(): return

  def exitContinueStmt(self, ctx: CompiscriptParser.ContinueStmtContext):
    if not self.continueCodeGeneration(): return

  def enterExprStmt(self, ctx: CompiscriptParser.ExprStmtContext):
    if not self.continueCodeGeneration(): return

  def exitExprStmt(self, ctx: CompiscriptParser.ExprStmtContext):
    if not self.continueCodeGeneration(): return

  def enterForStmt(self, ctx: CompiscriptParser.ForStmtContext):
    if not self.continueCodeGeneration(): return

  def exitForStmt(self, ctx: CompiscriptParser.ForStmtContext):
    if not self.continueCodeGeneration(): return

  def enterIfStmt(self, ctx: CompiscriptParser.IfStmtContext):
    if not self.continueCodeGeneration(): return

  def exitIfStmt(self, ctx: CompiscriptParser.IfStmtContext):
    if not self.continueCodeGeneration(): return

  def enterPrintStmt(self, ctx: CompiscriptParser.PrintStmtContext):
    if not self.continueCodeGeneration(): return

  def exitPrintStmt(self, ctx: CompiscriptParser.PrintStmtContext):
    if not self.continueCodeGeneration(): return

  def enterReturnStmt(self, ctx: CompiscriptParser.ReturnStmtContext):
    if not self.continueCodeGeneration(): return

  def exitReturnStmt(self, ctx: CompiscriptParser.ReturnStmtContext):
    if not self.continueCodeGeneration(): return

  def enterWhileStmt(self, ctx: CompiscriptParser.WhileStmtContext):
    if not self.continueCodeGeneration(): return

  def exitWhileStmt(self, ctx: CompiscriptParser.WhileStmtContext):
    if not self.continueCodeGeneration(): return

  def enterBlock(self, ctx: CompiscriptParser.BlockContext):
    if not self.continueCodeGeneration(): return

  def exitBlock(self, ctx: CompiscriptParser.BlockContext):
    if not self.continueCodeGeneration(): return

  def enterFunAnon(self, ctx: CompiscriptParser.FunAnonContext):
    if not self.continueCodeGeneration(): return

  def exitFunAnon(self, ctx: CompiscriptParser.FunAnonContext):
    if not self.continueCodeGeneration(): return

  def enterExpression(self, ctx: CompiscriptParser.ExpressionContext):
    if not self.continueCodeGeneration(): return

  def exitExpression(self, ctx: CompiscriptParser.ExpressionContext):
    if not self.continueCodeGeneration(): return
    
    ctx.addr = ctx.getChild(0).addr

  def enterAssignment(self, ctx: CompiscriptParser.AssignmentContext):
    if not self.continueCodeGeneration(): return

  def exitAssignment(self, ctx: CompiscriptParser.AssignmentContext):
    if not self.continueCodeGeneration(): return
    
    childNode = ctx.getChild(2)
    if childNode:
      print("nombre: ", childNode.getText())
      print(childNode.addr)
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return

  def enterLogic_or(self, ctx: CompiscriptParser.Logic_orContext):
    if not self.continueCodeGeneration(): return

  def exitLogic_or(self, ctx: CompiscriptParser.Logic_orContext):
    if not self.continueCodeGeneration(): return
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return

  def enterLogic_and(self, ctx: CompiscriptParser.Logic_andContext):
    if not self.continueCodeGeneration(): return

  def exitLogic_and(self, ctx: CompiscriptParser.Logic_andContext):
    if not self.continueCodeGeneration(): return
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return

  def enterEquality(self, ctx: CompiscriptParser.EqualityContext):
    if not self.continueCodeGeneration(): return

  def exitEquality(self, ctx: CompiscriptParser.EqualityContext):
    if not self.continueCodeGeneration(): return
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return

  def enterComparison(self, ctx: CompiscriptParser.ComparisonContext):
    if not self.continueCodeGeneration(): return

  def exitComparison(self, ctx: CompiscriptParser.ComparisonContext):
    if not self.continueCodeGeneration(): return
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return

  def enterTerm(self, ctx: CompiscriptParser.TermContext):
    if not self.continueCodeGeneration(): return

  def exitTerm(self, ctx: CompiscriptParser.TermContext):
    if not self.continueCodeGeneration(): return
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return

  def enterFactor(self, ctx: CompiscriptParser.FactorContext):
    if not self.continueCodeGeneration(): return

  def exitFactor(self, ctx: CompiscriptParser.FactorContext):
    if not self.continueCodeGeneration(): return
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return

  def enterArray(self, ctx: CompiscriptParser.ArrayContext):
    if not self.continueCodeGeneration(): return

  def exitArray(self, ctx: CompiscriptParser.ArrayContext):
    if not self.continueCodeGeneration(): return

  def enterInstantiation(self, ctx: CompiscriptParser.InstantiationContext):
    if not self.continueCodeGeneration(): return

  def exitInstantiation(self, ctx: CompiscriptParser.InstantiationContext):
    if not self.continueCodeGeneration(): return

  def enterUnary(self, ctx: CompiscriptParser.UnaryContext):
    if not self.continueCodeGeneration(): return

  def exitUnary(self, ctx: CompiscriptParser.UnaryContext):
    if not self.continueCodeGeneration(): return
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return

  def enterCall(self, ctx: CompiscriptParser.CallContext):
    if not self.continueCodeGeneration(): return

  def exitCall(self, ctx: CompiscriptParser.CallContext):
    if not self.continueCodeGeneration(): return
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return

  def enterPrimary(self, ctx: CompiscriptParser.PrimaryContext):
    if not self.continueCodeGeneration(): return

  def exitPrimary(self, ctx: CompiscriptParser.PrimaryContext):
    if not self.continueCodeGeneration(): return
    
    if len(ctx.children) == 1:
      # Un solo nodo hijo
      nodeType = ctx.type
      lexeme = ctx.getChild(0).getText()

      if isinstance(nodeType,(NumberType, StringType)):
        
        # Crear un nuevo temporal con valor
        temp = self.newTemp()
        # Guardar asignación en CI
        self.intermediateCode.add(result=temp, arg1=Value(lexeme, nodeType))
        ctx.addr = temp
        
      elif isinstance(nodeType, NilType):
        temp = self.newTemp()
        self.intermediateCode.add(result=temp, arg1=Value(None, NilType()))
        ctx.addr = temp
      
      elif isinstance(nodeType, (ObjectType, FunctionType, ClassType)):
        ctx.addr = nodeType
        
      
    else:
      pass
    
  def enterFunction(self, ctx: CompiscriptParser.FunctionContext):
    if not self.continueCodeGeneration(): return

  def exitFunction(self, ctx: CompiscriptParser.FunctionContext):
    if not self.continueCodeGeneration(): return

  def enterParameters(self, ctx: CompiscriptParser.ParametersContext):
    if not self.continueCodeGeneration(): return

  def exitParameters(self, ctx: CompiscriptParser.ParametersContext):
    if not self.continueCodeGeneration(): return

  def enterArguments(self, ctx: CompiscriptParser.ArgumentsContext):
    if not self.continueCodeGeneration(): return

  def exitArguments(self, ctx: CompiscriptParser.ArgumentsContext):
    if not self.continueCodeGeneration(): return
