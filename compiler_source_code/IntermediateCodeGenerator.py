from antlr.CompiscriptParser import CompiscriptParser
import uuid
from compoundTypes import ObjectType, FunctionType, ClassType, InstanceType, ClassSelfReferenceType, FunctionOverload
from primitiveTypes import NumberType, StringType, NilType, BoolType
from IntermediateCodeInstruction import SingleInstruction, EmptyInstruction, ConditionalInstruction
from consts import MEM_ADDR_SIZE
from Value import Value
from IntermediateCodeTokens import FUNCTION, GET_ARG, RETURN, PARAM, RETURN_VAL, CALL, MULTIPLY, MALLOC, EQUAL, GOTO, LABEL
from antlr4 import tree
from Offset import Offset

trueValue = Value(1, BoolType())
falseValue = Value(0, BoolType())
class IntermediateCodeGenerator():

  def __init__(self, symbolTable, semanticErrors = [], stopGeneration=False) -> None:
    self.symbolTable = symbolTable
    self.semanticErrors = semanticErrors
    self.tempCounter = 0
    self.labelCounter = 0
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
    label = f"L{self.labelCounter}"
    self.labelCounter += 1
    return label
  
  def getChildrenCode(self, ctx):
    """
    Concatenar todo el código de los hijos de un nodo.
    Retorna la primera instrucción de este bloque de código.
    """
    code = None
    for child in ctx.getChildren():
      if isinstance(child, tree.Tree.TerminalNode):
        continue
      if hasattr(child, "code"):
        if code == None:
          code = child.code
        else:
          code.concat(child.code)
          
    return code if code != None else EmptyInstruction()
    
  def enterProgram(self, ctx: CompiscriptParser.ProgramContext):
    if not self.continueCodeGeneration(): return

  def exitProgram(self, ctx: CompiscriptParser.ProgramContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    print("\nCódigo intermedio:\n", ctx.code.getFullCode())
    

  def enterDeclaration(self, ctx: CompiscriptParser.DeclarationContext):
    if not self.continueCodeGeneration(): return

  def exitDeclaration(self, ctx: CompiscriptParser.DeclarationContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)

  def enterClassDecl(self, ctx: CompiscriptParser.ClassDeclContext):
    if not self.continueCodeGeneration(): return

  def exitClassDecl(self, ctx: CompiscriptParser.ClassDeclContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)

  def enterFunDecl(self, ctx: CompiscriptParser.FunDeclContext):
    if not self.continueCodeGeneration(): return

  def exitFunDecl(self, ctx: CompiscriptParser.FunDeclContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)

  def enterVarDecl(self, ctx: CompiscriptParser.VarDeclContext):
    if not self.continueCodeGeneration(): return

  def exitVarDecl(self, ctx: CompiscriptParser.VarDeclContext, objectDef: ObjectType):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    expressionNode = ctx.expression()
    
    # Asignar un offset a la variable
    scope = self.symbolTable.currentScope
    objectDef.assignOffset(scope.offset, MEM_ADDR_SIZE)
    
    scope.setOffset(scope.offset + MEM_ADDR_SIZE) # Correr offset para siguiente variable
    
    if expressionNode is None:
      # Asignar NIL
      ctx.code.concat(SingleInstruction(result=objectDef, arg1=Value(None, NilType())))
    
    else:
      expressionAddr = expressionNode.addr
      ctx.code.concat(SingleInstruction(result=objectDef, arg1=expressionAddr))
    
    ctx.addr = objectDef
      


  def enterStatement(self, ctx: CompiscriptParser.StatementContext):
    if not self.continueCodeGeneration(): return

  def exitStatement(self, ctx: CompiscriptParser.StatementContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)

  def enterBreakStmt(self, ctx: CompiscriptParser.BreakStmtContext):
    if not self.continueCodeGeneration(): return

  def exitBreakStmt(self, ctx: CompiscriptParser.BreakStmtContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)

  def enterContinueStmt(self, ctx: CompiscriptParser.ContinueStmtContext):
    if not self.continueCodeGeneration(): return

  def exitContinueStmt(self, ctx: CompiscriptParser.ContinueStmtContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)

  def enterExprStmt(self, ctx: CompiscriptParser.ExprStmtContext):
    if not self.continueCodeGeneration(): return

  def exitExprStmt(self, ctx: CompiscriptParser.ExprStmtContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)

  def enterForStmt(self, ctx: CompiscriptParser.ForStmtContext):
    if not self.continueCodeGeneration(): return

  def exitForStmt(self, ctx: CompiscriptParser.ForStmtContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)

  def enterIfStmt(self, ctx: CompiscriptParser.IfStmtContext):
    if not self.continueCodeGeneration(): return

  def exitIfStmt(self, ctx: CompiscriptParser.IfStmtContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)

  def enterPrintStmt(self, ctx: CompiscriptParser.PrintStmtContext):
    if not self.continueCodeGeneration(): return

  def exitPrintStmt(self, ctx: CompiscriptParser.PrintStmtContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)

  def enterReturnStmt(self, ctx: CompiscriptParser.ReturnStmtContext):
    if not self.continueCodeGeneration(): return

  def exitReturnStmt(self, ctx: CompiscriptParser.ReturnStmtContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    returnVal = None
    expression = ctx.expression()

    if expression == None:
      # No tiene valor de retorno, nil por defecto
      returnVal = Value(None, NilType())
    
    else:
      returnVal = expression.addr
      
    ctx.code.concat(SingleInstruction(operator=RETURN, arg1=returnVal))

  def enterWhileStmt(self, ctx: CompiscriptParser.WhileStmtContext):
    if not self.continueCodeGeneration(): return

  def exitWhileStmt(self, ctx: CompiscriptParser.WhileStmtContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)

  def enterBlock(self, ctx: CompiscriptParser.BlockContext, parameters:list[ObjectType]=None):
    """
    Si parameters no es None, se trata de una función y se realiza la carga de los parametros.
    """
    if not self.continueCodeGeneration(): return
    
    scope = self.symbolTable.currentScope
    paramsCode = None
    # Correr offset para siguiente variable
    if parameters is not None:
      for i in range(len(parameters)):
        param = parameters[i]
        
        # Asignar un offset a la variable local que almacena params
        param.assignOffset(scope.offset, MEM_ADDR_SIZE)
        scope.setOffset(scope.offset + MEM_ADDR_SIZE)
        
        # Guardar código intermedio de asignación de parámetros
        instruction = SingleInstruction(result=param, operator=GET_ARG, arg1=str(i))
        if paramsCode is None:
          paramsCode = instruction
        else:
          paramsCode.concat(instruction)
    

  def exitBlock(self, ctx: CompiscriptParser.BlockContext, isFunctionBlock:bool):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    # Si se sale de una función, se genera un return nil por defecto
    if isFunctionBlock:
      ctx.code.concat(SingleInstruction(operator=RETURN, arg1=Value(None, NilType())))

  def enterFunAnon(self, ctx: CompiscriptParser.FunAnonContext, functionDef: FunctionType):
    if not self.continueCodeGeneration(): return


  def exitFunAnon(self, ctx: CompiscriptParser.FunAnonContext, functionDef: FunctionType):
    if not self.continueCodeGeneration(): return
    
    ctx.code = SingleInstruction(operator=FUNCTION, arg1=functionDef)    
    
    # Concatenar código de hijos
    ctx.code.concat(self.getChildrenCode(ctx))
    
    # Retornar dirección de función anónima
    ctx.addr = functionDef
    

  def enterExpression(self, ctx: CompiscriptParser.ExpressionContext):
    if not self.continueCodeGeneration(): return

  def exitExpression(self, ctx: CompiscriptParser.ExpressionContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    ctx.addr = ctx.getChild(0).addr

  def enterAssignment(self, ctx: CompiscriptParser.AssignmentContext):
    if not self.continueCodeGeneration(): return

  def exitAssignment(self, ctx: CompiscriptParser.AssignmentContext, objectDef: ObjectType = None):
    """
    Si objectDef no es None, se trata de una asignación a una variable
    """
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
      
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return
    
    valueAddr = ctx.assignment().addr
    ctx.addr = valueAddr
    
    if objectDef is not None:
      # Si es una asignación a una variable
      ctx.code.concat(SingleInstruction(result=objectDef, arg1=valueAddr))
    else:
      # Si es una asignación a un atributo de clase
      raise NotImplementedError("Asignación a atributo de clase en CI no implementada")


  def enterLogic_or(self, ctx: CompiscriptParser.Logic_orContext):
    if not self.continueCodeGeneration(): return

  def exitLogic_or(self, ctx: CompiscriptParser.Logic_orContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return
    
    # Operación lógica or
    
    code = None
    operand1 = None
    
    trueLabel = self.newLabel()
    endLabel = self.newLabel()
    
    for child in ctx.children:
      if isinstance(child, CompiscriptParser.Logic_andContext):
        
        operand1 = child.addr
        
        conditionalCode = ConditionalInstruction(arg1=operand1, operator=EQUAL, arg2=trueValue, goToLabel=trueLabel)
        if code == None:
          code = conditionalCode
        else:
          code.concat(conditionalCode)
          
    temp = self.newTemp()
    # Si ningún operando es true, asignar falseVal a temporal y saltar al final
    code.concat(SingleInstruction(result=temp, arg1=falseValue))
    code.concat(SingleInstruction(operator=GOTO, arg1=endLabel))
    
    # Etiqueta de true: asignar trueVal a temporal
    code.concat(SingleInstruction(operator=LABEL, arg1=trueLabel))
    code.concat(SingleInstruction(result=temp, arg1=trueValue))
    
    # Etiqueta de fin
    code.concat(SingleInstruction(operator=LABEL, arg1=endLabel))
    
    # Guardar addr de resultado de operación and y concatenar código
    ctx.addr = temp
    ctx.code.concat(code)

  def enterLogic_and(self, ctx: CompiscriptParser.Logic_andContext):
    if not self.continueCodeGeneration(): return

  def exitLogic_and(self, ctx: CompiscriptParser.Logic_andContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return
    
    # Operación lógica and
    
    code = None
    operand1 = None
    
    falseLabel = self.newLabel()
    endLabel = self.newLabel()
    
    for child in ctx.children:
      if isinstance(child, CompiscriptParser.EqualityContext):
        
        operand1 = child.addr
        

        conditionalCode = ConditionalInstruction(arg1=operand1, operator=EQUAL, arg2=falseValue, goToLabel=falseLabel)
        if code == None:
          code = conditionalCode
        else:
          code.concat(conditionalCode)
          
    temp = self.newTemp()
    # Si ningún operando es false, asignar trueVal a temporal y saltar al final
    code.concat(SingleInstruction(result=temp, arg1=trueValue))
    code.concat(SingleInstruction(operator=GOTO, arg1=endLabel))
    
    # Etiqueta de falso: asignar falseVal a temporal
    code.concat(SingleInstruction(operator=LABEL, arg1=falseLabel))
    code.concat(SingleInstruction(result=temp, arg1=falseValue))
    
    # Etiqueta de fin
    code.concat(SingleInstruction(operator=LABEL, arg1=endLabel))
    
    # Guardar addr de resultado de operación and y concatenar código
    ctx.addr = temp
    ctx.code.concat(code)
    
    

  def enterEquality(self, ctx: CompiscriptParser.EqualityContext):
    if not self.continueCodeGeneration(): return

  def exitEquality(self, ctx: CompiscriptParser.EqualityContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return

  def enterComparison(self, ctx: CompiscriptParser.ComparisonContext):
    if not self.continueCodeGeneration(): return

  def exitComparison(self, ctx: CompiscriptParser.ComparisonContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return

  def enterTerm(self, ctx: CompiscriptParser.TermContext):
    if not self.continueCodeGeneration(): return

  def exitTerm(self, ctx: CompiscriptParser.TermContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return

  def enterFactor(self, ctx: CompiscriptParser.FactorContext):
    if not self.continueCodeGeneration(): return

  def exitFactor(self, ctx: CompiscriptParser.FactorContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return

  def enterArray(self, ctx: CompiscriptParser.ArrayContext):
    if not self.continueCodeGeneration(): return

  def exitArray(self, ctx: CompiscriptParser.ArrayContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    # Si está vacío, asignar como nil
    if len(ctx.expression()) == 0:
      arrayAddr = self.newTemp()
      ctx.code.concat(SingleInstruction(result=arrayAddr, arg1=Value(None, NilType())))
      ctx.addr = arrayAddr
      return
    
    ctx.addr = None
    
    array_size = len(ctx.expression()) * MEM_ADDR_SIZE
    
    # Guardar array en memoria dinamica
    arrayAddr = self.newTemp() # Temp guarda dirección de inicio de array
    arrayCode = SingleInstruction(result=arrayAddr, arg1=array_size, operator=MALLOC)
    
    for index, expression in enumerate(ctx.expression()):
      arrayPosition = Offset(arrayAddr, index * MEM_ADDR_SIZE) # Dirección de memoria del elemento en el array
      arrayCode.concat(SingleInstruction(result=arrayPosition, arg1=expression.addr))

    ctx.addr = arrayAddr
    ctx.code.concat(arrayCode)
    
    
  def enterInstantiation(self, ctx: CompiscriptParser.InstantiationContext):
    if not self.continueCodeGeneration(): return

  def exitInstantiation(self, ctx: CompiscriptParser.InstantiationContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)

  def enterUnary(self, ctx: CompiscriptParser.UnaryContext):
    if not self.continueCodeGeneration(): return

  def exitUnary(self, ctx: CompiscriptParser.UnaryContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return

  def enterCall(self, ctx: CompiscriptParser.CallContext):
    if not self.continueCodeGeneration(): return

  def exitCall(self, ctx: CompiscriptParser.CallContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
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
          code = SingleInstruction(operator=CALL, arg1=functionDef, arg2=obtainedParams, operatorFirst=True)
          
          # Crear un nuevo temporal para guardar el valor de retorno
          offset = self.newTemp()
          code.concat(SingleInstruction(result=offset, arg1=RETURN_VAL))
          
          # Asignar valor de retorno como addr
          ctx.addr = offset
          # Concatenar código
          ctx.code.concat(code)

        elif lexeme == ".":
          
          # Se está accediendo a un atributo de clase
          raise NotImplementedError("exitCall: Acceso a atributo de clase en CI no implementado")

        elif lexeme == "[":

          # Se está accediendo a un elemento de un array
          
          arrayBase = nodeAddr
          
          indexToken = ctx.expression(0)
          
          # Calcular el desplazamiento: indice * tamaño de casilla
          arrayShiftTemp = self.newTemp()
          ctx.code.concat(SingleInstruction(result=arrayShiftTemp, arg1=indexToken.addr, arg2=MEM_ADDR_SIZE, operator=MULTIPLY))
          
          # Asignar array[arrayShift] a addr
          arrayElement = Offset(arrayBase, arrayShiftTemp)
                
          ctx.addr = arrayElement
          
          



  def enterPrimary(self, ctx: CompiscriptParser.PrimaryContext):
    if not self.continueCodeGeneration(): return

  def exitPrimary(self, ctx: CompiscriptParser.PrimaryContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
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
        ctx.code.concat(SingleInstruction(result=temp, arg1=Value(lexeme, nodeType)))
        ctx.addr = temp
        
      elif isinstance(nodeType, NilType):
        temp = self.newTemp()
        ctx.code.concat(SingleInstruction(result=temp, arg1=Value(None, NilType())))
        ctx.addr = temp
        
      elif isinstance(nodeType, BoolType):
        temp = self.newTemp()
        
        val = trueValue if lexeme == "true" else falseValue
        ctx.code.concat(SingleInstruction(result=temp, arg1=val))
        ctx.addr = temp
      
      elif isinstance(nodeType, (ObjectType, FunctionType,FunctionOverload, ClassType)):
        ctx.addr = nodeType
        
      
    else:
      pass
    
  def enterFunction(self, ctx: CompiscriptParser.FunctionContext, functionDef: FunctionType):
    if not self.continueCodeGeneration(): return
    

  def exitFunction(self, ctx: CompiscriptParser.FunctionContext, functionDef: FunctionType):
    if not self.continueCodeGeneration(): return
    ctx.code = SingleInstruction(operator=FUNCTION, arg1=functionDef)
    ctx.code.concat(self.getChildrenCode(ctx))
    

  def enterParameters(self, ctx: CompiscriptParser.ParametersContext, functionDef: FunctionType):
    if not self.continueCodeGeneration(): return
    
    # Asignación de parámetros se realiza en enterBlock

  def exitParameters(self, ctx: CompiscriptParser.ParametersContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)

  def enterArguments(self, ctx: CompiscriptParser.ArgumentsContext):
    if not self.continueCodeGeneration(): return

  def exitArguments(self, ctx: CompiscriptParser.ArgumentsContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    for expression in ctx.expression():
      # Agregar CI de argumentos
      ctx.code.concat(SingleInstruction(operator=PARAM, arg1=expression.addr))
