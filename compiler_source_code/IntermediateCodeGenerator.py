from antlr.CompiscriptParser import CompiscriptParser
import uuid
from compoundTypes import ObjectType, FunctionType, ClassType, InstanceType, ClassSelfReferenceType, FunctionOverload
from primitiveTypes import NumberType, StringType, NilType
from IntermediateCodeQuadruple import IntermediateCodeQuadruple
from consts import MEM_ADDR_SIZE
from Value import Value
from IntermediateCodeTokens import FUNCTION, GET_ARG, RETURN, PARAM, RETURN_VAL, CALL, MULTIPLY, PLUS, BASE_POINTER, MALLOC
from antlr4 import tree
from Offset import Offset


class IntermediateCodeGenerator():

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
    #tempName = f"t{self.tempCounter}-{uuid.uuid4()}"
    tempName = f"t{self.tempCounter}"
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
    
    returnVal = None
    expression = ctx.expression()

    if expression == None:
      # No tiene valor de retorno, nil por defecto
      returnVal = Value(None, NilType())
    
    else:
      returnVal = expression.addr
      
    self.intermediateCode.add(operator=RETURN, arg1=returnVal)

  def enterWhileStmt(self, ctx: CompiscriptParser.WhileStmtContext):
    if not self.continueCodeGeneration(): return

  def exitWhileStmt(self, ctx: CompiscriptParser.WhileStmtContext):
    if not self.continueCodeGeneration(): return

  def enterBlock(self, ctx: CompiscriptParser.BlockContext, parameters:list[ObjectType]=None):
    """
    Si parameters no es None, se trata de una función y se realiza la carga de los parametros.
    """
    if not self.continueCodeGeneration(): return
    
    scope = self.symbolTable.currentScope
    # Correr offset para siguiente variable
    if parameters is not None:
      for i in range(len(parameters)):
        param = parameters[i]
        
        # Asignar un offset a la variable local que almacena params
        param.assignOffset(scope.offset, MEM_ADDR_SIZE)
        scope.setOffset(scope.offset + MEM_ADDR_SIZE)
        
        # Guardar código intermedio de asignación de parámetros
        self.intermediateCode.add(result=param, operator=GET_ARG, arg1=str(i))
    

  def exitBlock(self, ctx: CompiscriptParser.BlockContext, isFunctionBlock:bool):
    if not self.continueCodeGeneration(): return
    
    # Si se sale de una función, se genera un return nil por defecto
    if isFunctionBlock:
      self.intermediateCode.add(operator=RETURN, arg1=Value(None, NilType()))

  def enterFunAnon(self, ctx: CompiscriptParser.FunAnonContext, functionDef: FunctionType):
    if not self.continueCodeGeneration(): return
    
    # Añadir CI de función anónima
    self.intermediateCode.add(operator=FUNCTION, arg1=functionDef)

  def exitFunAnon(self, ctx: CompiscriptParser.FunAnonContext, functionDef: FunctionType):
    if not self.continueCodeGeneration(): return
    
    # Retornar dirección de función anónima
    ctx.addr = functionDef
    

  def enterExpression(self, ctx: CompiscriptParser.ExpressionContext):
    if not self.continueCodeGeneration(): return

  def exitExpression(self, ctx: CompiscriptParser.ExpressionContext):
    if not self.continueCodeGeneration(): return
    
    ctx.addr = ctx.getChild(0).addr

  def enterAssignment(self, ctx: CompiscriptParser.AssignmentContext):
    if not self.continueCodeGeneration(): return

  def exitAssignment(self, ctx: CompiscriptParser.AssignmentContext, objectDef: ObjectType = None):
    """
    Si objectDef no es None, se trata de una asignación a una variable
    """
    if not self.continueCodeGeneration(): return
      
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return
    
    valueAddr = ctx.assignment().addr
    ctx.addr = valueAddr
    
    if objectDef is not None:
      # Si es una asignación a una variable
      self.intermediateCode.add(result=objectDef, arg1=valueAddr)
    else:
      # Si es una asignación a un atributo de clase
      raise NotImplementedError("Asignación a atributo de clase en CI no implementada")


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
    
    # Si está vacío, asignar como nil
    if len(ctx.expression()) == 0:
      arrayAddr = self.newTemp()
      self.intermediateCode.add(result=arrayAddr, arg1=Value(None, NilType()))
      ctx.addr = arrayAddr
      return
    
    ctx.addr = None
    
    array_size = len(ctx.expression()) * MEM_ADDR_SIZE
    
    # Guardar array en memoria dinamica
    arrayAddr = self.newTemp() # Temp guarda dirección de inicio de array
    self.intermediateCode.add(result=arrayAddr, arg1=array_size, operator=MALLOC)
    
    for index, expression in enumerate(ctx.expression()):
      arrayPosition = Offset(arrayAddr, index * MEM_ADDR_SIZE) # Dirección de memoria del elemento en el array
      self.intermediateCode.add(result=arrayPosition, arg1=expression.addr)

    ctx.addr = arrayAddr
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
    
    nodeAddr = None

    for index, child in enumerate(ctx.getChildren()):     
      
      if isinstance(child, CompiscriptParser.PrimaryContext):
        # Obtener el addr del nodo primario (identificador)
        primary_context = ctx.primary()
        
        nodeAddr = primary_context.addr

      elif isinstance(child, tree.Tree.TerminalNode):

        token = child.getSymbol()
        lexeme = child.getText()
        line = token.line
        column = token.column 

        if lexeme == "(":
            
          obtainedParams = 0 if ctx.arguments(0) == None else len(ctx.arguments(0).expression())
          
          functionDef = nodeAddr
          
          # Si la función es una sobrecarga, obtener la función que corresponde a los argumentos
          if nodeAddr.strictEqualsType(FunctionOverload):
            functionDef = nodeAddr.getFunctionByParams(obtainedParams)

          # Añadir Ci de llamada a función
          self.intermediateCode.add(operator=CALL, arg1=functionDef, arg2=obtainedParams, operatorFirst=True)
          
          # Crear un nuevo temporal para guardar el valor de retorno
          offset = self.newTemp()
          self.intermediateCode.add(result=offset, arg1=RETURN_VAL)
          
          # Asignar valor de retorno como addr
          ctx.addr = offset

        elif lexeme == ".":
          
          # Se está accediendo a un atributo de clase
          raise NotImplementedError("exitCall: Acceso a atributo de clase en CI no implementado")

        elif lexeme == "[":

          # Se está accediendo a un elemento de un array
          
          arrayBase = nodeAddr
          
          indexToken = ctx.expression(0)
          
          # Calcular el desplazamiento: indice * tamaño de casilla
          arrayShiftTemp = self.newTemp()
          self.intermediateCode.add(result=arrayShiftTemp, arg1=indexToken.addr, arg2=MEM_ADDR_SIZE, operator=MULTIPLY)
          
          # Asignar array[arrayShift] a addr
          arrayElement = Offset(arrayBase, arrayShiftTemp)
                
          ctx.addr = arrayElement
          
          



  def enterPrimary(self, ctx: CompiscriptParser.PrimaryContext):
    if not self.continueCodeGeneration(): return

  def exitPrimary(self, ctx: CompiscriptParser.PrimaryContext):
    if not self.continueCodeGeneration(): return
    
    if len(ctx.children) == 1:
      # Un solo nodo hijo
      nodeType = ctx.type
      lexeme = ctx.getChild(0).getText()
      
      if not isinstance(ctx.getChild(0), tree.Tree.TerminalNode):
        # Es un no terminal
        ctx.addr = ctx.getChild(0).addr

      elif isinstance(nodeType,(NumberType, StringType)):
        
        # Crear un nuevo temporal con valor
        temp = self.newTemp()
        # Guardar asignación en CI
        self.intermediateCode.add(result=temp, arg1=Value(lexeme, nodeType))
        ctx.addr = temp
        
      elif isinstance(nodeType, NilType):
        temp = self.newTemp()
        self.intermediateCode.add(result=temp, arg1=Value(None, NilType()))
        ctx.addr = temp
      
      elif isinstance(nodeType, (ObjectType, FunctionType,FunctionOverload, ClassType)):
        ctx.addr = nodeType
        
      
    else:
      pass
    
  def enterFunction(self, ctx: CompiscriptParser.FunctionContext, functionDef: FunctionType):
    if not self.continueCodeGeneration(): return
    
    self.intermediateCode.add(operator=FUNCTION, arg1=functionDef)

  def exitFunction(self, ctx: CompiscriptParser.FunctionContext):
    if not self.continueCodeGeneration(): return

  def enterParameters(self, ctx: CompiscriptParser.ParametersContext, functionDef: FunctionType):
    if not self.continueCodeGeneration(): return
    
    # Asignación de parámetros se realiza en enterBlock

  def exitParameters(self, ctx: CompiscriptParser.ParametersContext):
    if not self.continueCodeGeneration(): return

  def enterArguments(self, ctx: CompiscriptParser.ArgumentsContext):
    if not self.continueCodeGeneration(): return

  def exitArguments(self, ctx: CompiscriptParser.ArgumentsContext):
    if not self.continueCodeGeneration(): return
    
    for expression in ctx.expression():
      # Agregar CI de argumentos
      self.intermediateCode.add(operator=PARAM, arg1=expression.addr)
