from antlr.CompiscriptParser import CompiscriptParser
import uuid
from compoundTypes import ObjectType, FunctionType, ClassType, InstanceType, ClassSelfReferenceType, FunctionOverload, SuperMethodWrapper
from primitiveTypes import NumberType, StringType, NilType, BoolType, AnyType, FloatType, IntType
from IntermediateCodeInstruction import SingleInstruction, EmptyInstruction, ConditionalInstruction
from consts import MEM_ADDR_SIZE, MAX_PROPERTIES
from Value import Value
from IntermediateCodeTokens import FUNCTION, GET_ARG, RETURN, PARAM, RETURN_VAL, CALL, MULTIPLY, MALLOC, EQUAL, NOT_EQUAL, NOT, LESS, LESS_EQUAL, GOTO, LABEL, MINUS, XOR, MOD, DIVIDE, PLUS, PRINT, CONCAT, END_FUNCTION
from antlr4 import tree
from Offset import Offset
from ParamsTree import ParamsTree
from SymbolTable import ScopeType

trueValue = Value(1, BoolType())
falseValue = Value(0, BoolType())
class IntermediateCodeGenerator():

  def __init__(self, symbolTable, semanticErrors = [], stopGeneration=False) -> None:
    self.symbolTable = symbolTable
    self.semanticErrors = semanticErrors
    self.tempCounter = 0
    self.labelCounter = 0
    self.stopGeneration = stopGeneration
    
    self.loopParams = ParamsTree() # Almacena labels de inicio y fin de loops
    self.thisReferenceParams = ParamsTree() # Almacena referencias a this en métodos
    
    self.programCode = None
  
  def continueCodeGeneration(self):
    return not self.stopGeneration and len(self.semanticErrors) == 0 
    
  def newTemp(self, type = AnyType()):
    """
    Crea un nuevo temporal y lo agrega a la tabla de simbolos
    value: debe ser un valor primitivo o un ObjectType
    """
    #tempName = f"t{self.tempCounter}-{uuid.uuid4()}"
    tempName = f"t{self.tempCounter}"
    self.tempCounter += 1
    temp = self.symbolTable.currentScope.addTemporary(tempName, type)
    
    # Asignar un offset al temporal
    scope = self.symbolTable.currentScope
    temp.assignOffset(scope.getOffset(), MEM_ADDR_SIZE)
    # Correr offset para siguiente variable
    scope.setOffset(scope.getOffset() + MEM_ADDR_SIZE)
    
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
  
  def getProgramCode(self):
    if self.programCode == None:
      return None
    return self.programCode.getFullCode()
    
  def enterProgram(self, ctx: CompiscriptParser.ProgramContext):
    if not self.continueCodeGeneration(): return

  def exitProgram(self, ctx: CompiscriptParser.ProgramContext):
    if not self.continueCodeGeneration(): return
    self.programCode = self.getChildrenCode(ctx)

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
    objectDef.assignOffset(scope.getOffset(), MEM_ADDR_SIZE)
    
    scope.setOffset(scope.getOffset() + MEM_ADDR_SIZE) # Correr offset para siguiente variable
    
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
    
    # obtener label de fin de loop
    currentParams = self.loopParams.getParams()
    endLabel = currentParams.get("endLabel")
    
    # Añadir código de salto a fin de loop
    ctx.code.concat(SingleInstruction(operator=GOTO, arg1=endLabel))

  def enterContinueStmt(self, ctx: CompiscriptParser.ContinueStmtContext):
    if not self.continueCodeGeneration(): return

  def exitContinueStmt(self, ctx: CompiscriptParser.ContinueStmtContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    # obtener label de inicio de loop
    currentParams = self.loopParams.getParams()
    repeatLabel = currentParams.get("repeatLabel")
    
    # Añadir código de salto a inicio de loop
    ctx.code.concat(SingleInstruction(operator=GOTO, arg1=repeatLabel))

  def enterExprStmt(self, ctx: CompiscriptParser.ExprStmtContext):
    if not self.continueCodeGeneration(): return

  def exitExprStmt(self, ctx: CompiscriptParser.ExprStmtContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)

  def enterForStmt(self, ctx: CompiscriptParser.ForStmtContext):
    if not self.continueCodeGeneration(): return
    
    # Se guaran en el nodo los labels de inicio y fin de loop
    repeatLabel = self.newLabel()
    endLabel = self.newLabel()
    
    # Guardar labels de inicio y fin de loop para hijos
    _, currentParams = self.loopParams.initNodeParams()
    currentParams.add("repeatLabel", repeatLabel)
    currentParams.add("endLabel", endLabel)

  def exitForStmt(self, ctx: CompiscriptParser.ForStmtContext):
    if not self.continueCodeGeneration(): return
    
    # Determinar posición de último ; y ), que son los limites de la expresión de actualización
    updateExpressionLimits = [None, None]
    for i, child in enumerate(ctx.children):
      if child.getText() == ";":
        updateExpressionLimits[0] = i
      elif child.getText() == ")":
        updateExpressionLimits[1] = i
    
    # Si solo hay una expresión y hay más de un elemento entre último ; y ) (no son índices continuos)
    # es la expresion de actualización. De lo contrario, es la condición
    hasConditionExpression = len(ctx.expression()) > 0 and (len(ctx.expression()) == 2 or updateExpressionLimits[1] - updateExpressionLimits[0] == 1)
    hasUpdateExpression = len(ctx.expression()) > 0 and (len(ctx.expression()) == 2 or updateExpressionLimits[1] - updateExpressionLimits[0] > 1)
    
    code = None
    
    if ctx.varDecl() != None or ctx.exprStmt() != None:
      # Hay una declaración (o asignación de variable), añadir su código
      initializationCode = ctx.varDecl().code if ctx.varDecl() != None else ctx.exprStmt().code
      code = initializationCode
    
    # Obtener labels de inicio y fin de loop, eliminandolos del arbol de params
    currentParams = self.loopParams.removeNodeParams()
    repeatLabel = currentParams.get("repeatLabel")
    endLabel = currentParams.get("endLabel")
    
    # Agregar etiqueta de inicio de loop
    repeatLabelInstruction = SingleInstruction(operator=LABEL, arg1=repeatLabel)
    if code == None:
      code = repeatLabelInstruction
    else:
      code.concat(repeatLabelInstruction)
      
    
    # Realizar la evaluación de la condición (si la hay)
    if hasConditionExpression:
      # Existe una condición
      conditionExpression = ctx.expression(0)
      
      # Agregar código de condición
      code.concat(conditionExpression.code)
      
      # Si la condición es falsa, saltar al final
      code.concat(ConditionalInstruction(arg1=conditionExpression.addr, operator=EQUAL, arg2=falseValue, goToLabel=endLabel))
      
    
    # Concatenar código de statement
    statementCode = ctx.statement().code
    code.concat(statementCode)
    
    # Agregar expresión de actualización (si la hay)
    if hasUpdateExpression:
      updateExpressionIndex = 1 if hasConditionExpression else 0
      updateExpression = ctx.expression(updateExpressionIndex)
      code.concat(updateExpression.code)
    
    # Saltar al inicio del loop
    code.concat(SingleInstruction(operator=GOTO, arg1=repeatLabel))
    
    # Etiqueta de fin
    code.concat(SingleInstruction(operator=LABEL, arg1=endLabel))
    
    ctx.code = code
    

  def enterIfStmt(self, ctx: CompiscriptParser.IfStmtContext):
    if not self.continueCodeGeneration(): return

  def exitIfStmt(self, ctx: CompiscriptParser.IfStmtContext):
    if not self.continueCodeGeneration(): return
    
    hasElseStatement = len(ctx.statement()) > 1
    
    expressionNode = ctx.expression()
    expression = expressionNode.addr
    statementCode = ctx.statement(0).code
    
    ctx.code = expressionNode.code # Agregar código necesario para evaluar la expresión
    
    skipLabel = self.newLabel()
    endLabel = self.newLabel()
    
    # Si la condición es falsa, saltar al final
    conditionalCode = ConditionalInstruction(arg1=expression, operator=EQUAL, arg2=falseValue, goToLabel=skipLabel)
    conditionalCode.concat(statementCode)
    conditionalCode.concat(SingleInstruction(operator=GOTO, arg1=endLabel)) # Evitar else (si existe)
    conditionalCode.concat(SingleInstruction(operator=LABEL, arg1=skipLabel)) # Evitar if statement
    
    # Si hay else, ejecutarlo
    if hasElseStatement:
      elseStatementCode = ctx.statement(1).code
      conditionalCode.concat(elseStatementCode)
      
    # Etiqueta de fin
    conditionalCode.concat(SingleInstruction(operator=LABEL, arg1=endLabel))
    
    ctx.code.concat(conditionalCode)    
    
    
  def enterPrintStmt(self, ctx: CompiscriptParser.PrintStmtContext):
    if not self.continueCodeGeneration(): return

  def exitPrintStmt(self, ctx: CompiscriptParser.PrintStmtContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    ctx.code.concat(SingleInstruction(operator=PRINT, arg1=ctx.expression().addr))

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
    
    # Se guaran en el nodo los labels de inicio y fin de loop
    repeatLabel = self.newLabel()
    endLabel = self.newLabel()
    
    # Guardar labels de inicio y fin de loop para hijos
    _, currentParams = self.loopParams.initNodeParams()
    currentParams.add("repeatLabel", repeatLabel)
    currentParams.add("endLabel", endLabel)    

  def exitWhileStmt(self, ctx: CompiscriptParser.WhileStmtContext):
    if not self.continueCodeGeneration(): return
    
    expressionNode = ctx.expression()
    expression = expressionNode.addr
    statementCode = ctx.statement().code
    
    # Obtener labels de inicio y fin de loop, eliminandolos del arbol de params
    currentParams = self.loopParams.removeNodeParams()
    repeatLabel = currentParams.get("repeatLabel")
    endLabel = currentParams.get("endLabel")
    
    # Label para repetir loop
    whileCode = SingleInstruction(operator=LABEL, arg1=repeatLabel)
    
    # Realizar la evaluación de la expresión
    whileCode.concat(expressionNode.code)
    
    # Si la condición es falsa, saltar al final
    whileCode.concat(ConditionalInstruction(arg1=expression, operator=EQUAL, arg2=falseValue, goToLabel=endLabel))
    
    # Concatenar código de statement
    whileCode.concat(statementCode)
    
    # Saltar al inicio del loop
    whileCode.concat(SingleInstruction(operator=GOTO, arg1=repeatLabel))
    
    # Etiqueta de fin
    whileCode.concat(SingleInstruction(operator=LABEL, arg1=endLabel))
    
    ctx.code = whileCode

  def enterBlock(self, ctx: CompiscriptParser.BlockContext, parameters:list[ObjectType]=None):
    """
    Si parameters no es None, se trata de una función y se realiza la carga de los parametros.
    """
    if not self.continueCodeGeneration(): return
    
    scope = self.symbolTable.currentScope
    if scope.isMethodScope():
        # Si es un método, crear temporal que guarda referencia a this y guardarla en params
        
        thisTemp = self.newTemp()

        # Guardar referencia a this en arbol de parámetros
        _, currentParams = self.thisReferenceParams.initNodeParams()
        currentParams.add("this", thisTemp)
    

  def exitBlock(self, ctx: CompiscriptParser.BlockContext):
    if not self.continueCodeGeneration(): return
    
    paramsCode = None
    
    scope = self.symbolTable.currentScope
    if scope.type == ScopeType.FUNCTION or scope.type == ScopeType.CONSTRUCTOR:
      
      functionDef = scope.reference
      
      paramsCount = 0
      
      if scope.isMethodScope():
        # Si es un método, obtener temporal que guarda referencia a this y eliminarla del arbol de parámetros
        currentParams = self.thisReferenceParams.removeNodeParams()
        thisTemp = currentParams.get("this")
    
        # Guardar código intermedio de asignación de this
        paramsCode = SingleInstruction(result=thisTemp, operator=GET_ARG, arg1="0")
        
        paramsCount += 1

      # Código intermedio de asignación de parametros
      for i, param in enumerate(functionDef.params):
        
        param = scope.searchElement(param, searchInParentScopes = False, searchInParentClasses = False, searchTemporaries = False)
        
        # Asignar un offset a la variable local que almacena params
        param.assignOffset(scope.getOffset(), MEM_ADDR_SIZE)
        scope.setOffset(scope.getOffset() + MEM_ADDR_SIZE)
        
        # Guardar código intermedio de asignación de parámetros
        instruction = SingleInstruction(result=param, operator=GET_ARG, arg1=str(paramsCount + i))
        if paramsCode is None:
          paramsCode = instruction
        else:
          paramsCode.concat(instruction)

      ctx.code = paramsCode
      
      # Añadir código de hijos (concatenado a declaración de parámetros)
      if ctx.code == None:
        ctx.code = self.getChildrenCode(ctx)
      else:
        ctx.code.concat(self.getChildrenCode(ctx))
      
      # Si se sale de una función, se genera un return nil por defecto
      ctx.code.concat(SingleInstruction(operator=RETURN, arg1=Value(None, NilType())))
      
      # Indicar fin de función
      ctx.code.concat(SingleInstruction(operator=END_FUNCTION, arg1=functionDef))

    else:
      # Si no es una función, concatenar código de hijos
      ctx.code = self.getChildrenCode(ctx)
      
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
    valueType = ctx.assignment().type
    ctx.addr = valueAddr
    
    if objectDef is not None:
      # Si es una asignación a una variable
      ctx.code.concat(SingleInstruction(result=objectDef, arg1=valueAddr))
      
    elif not valueType.strictEqualsType(FunctionType): # Ignorar métodos (no se pueden asignar)
      
      # Es una asignación de atributo
      callNode = ctx.call()
      identifier = ctx.IDENTIFIER().getText()
            
      if callNode.type.strictEqualsType(ClassSelfReferenceType):
        # Es una asignación dentro de la definición de la clase (this)
        
        classSelfReference = callNode.type
        thisTemp = callNode.addr # Dirección de memoria del bloque del objeto correspondiente
        
        # Realizar offset relativo a la dirección de memoria del objeto
        propertyIndex = classSelfReference.getPropertyIndex(identifier)
        propertyPosition = Offset(thisTemp, propertyIndex * MEM_ADDR_SIZE)
        
        # Asignar valor a propiedad en CI
        ctx.code.concat(SingleInstruction(result=propertyPosition, arg1=valueAddr))
        
      else:
        
        # Es una asignación a un objeto ya instanciado
        instanceAddr = callNode.addr
        instanceType = callNode.type.getType()
        
        # Realizar offset relativo a la dirección de memoria del objeto
        propertyIndex = instanceType.getPropertyIndex(identifier)
        propertyPosition = Offset(instanceAddr, propertyIndex * MEM_ADDR_SIZE)
        
        # Asignar valor a propiedad en CI
        ctx.code.concat(SingleInstruction(result=propertyPosition, arg1=valueAddr))
      


  def enterLogic_or(self, ctx: CompiscriptParser.Logic_orContext):
    if not self.continueCodeGeneration(): return

  def exitLogic_or(self, ctx: CompiscriptParser.Logic_orContext):
    if not self.continueCodeGeneration(): return
        
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      ctx.code = self.getChildrenCode(ctx)
      return
    
    # Operación lógica or
    
    code = None
    operand1 = None
    
    trueLabel = self.newLabel()
    endLabel = self.newLabel()
    
    for child in ctx.children:
      if isinstance(child, CompiscriptParser.Logic_andContext):
        
        # Agregar código para evaluar expresión
        if code == None:
          code = child.code
        else:
          code.concat(child.code)
          
        operand1 = child.addr
        
        # Si el operando es true, saltar al final y no seguir evaluando
        conditionalCode = ConditionalInstruction(arg1=operand1, operator=EQUAL, arg2=trueValue, goToLabel=trueLabel)
        code.concat(conditionalCode)
          
    temp = self.newTemp(BoolType())
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
    ctx.code = code
  def enterLogic_and(self, ctx: CompiscriptParser.Logic_andContext):
    if not self.continueCodeGeneration(): return

  def exitLogic_and(self, ctx: CompiscriptParser.Logic_andContext):
    if not self.continueCodeGeneration(): return
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      ctx.code = self.getChildrenCode(ctx)
      return
    
    # Operación lógica and
    
    code = None
    operand1 = None
    
    falseLabel = self.newLabel()
    endLabel = self.newLabel()
    
    for child in ctx.children:
      if isinstance(child, CompiscriptParser.EqualityContext):
        
        # Agregar código para evaluar expresión
        if code == None:
          code = child.code
        else:
          code.concat(child.code)
        
        operand1 = child.addr

        # Si el operando es false, saltar al final y no seguir evaluando
        conditionalCode = ConditionalInstruction(arg1=operand1, operator=EQUAL, arg2=falseValue, goToLabel=falseLabel)
        code.concat(conditionalCode)
          
    temp = self.newTemp(BoolType())
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
    ctx.code = code
    
    

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
    
    # Operación de comparación
    code = None
    numOperations = (len(ctx.children) - 1) // 2
    
    temp = self.newTemp(BoolType())
    
    for i in range(numOperations):
      
      firstOperandIndex = i * 2
      operand1 = ctx.getChild(firstOperandIndex).addr
      operatorLexeme = ctx.getChild(firstOperandIndex + 1).getText()
      operand2 = ctx.getChild(firstOperandIndex + 2).addr
      
      operator = EQUAL if operatorLexeme == "==" else NOT_EQUAL
      instruction = SingleInstruction(result=temp, arg1=operand1, operator=operator, arg2=operand2)
      
      if code == None:
        code = instruction
      else:
        code.concat(instruction)
        
    # Guardar addr de resultado de operación de comparación y concatenar código
    ctx.addr = temp
    ctx.code.concat(code)

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
    
    
    # Comparación
    
    code = None
    numOperations = (len(ctx.children) - 1) // 2
  
    temp = self.newTemp(BoolType())
    
    for i in range(numOperations):
      
      firstOperandIndex = i * 2
      operand1 = ctx.getChild(firstOperandIndex).addr
      operator = ctx.getChild(firstOperandIndex + 1).getText()
      operand2 = ctx.getChild(firstOperandIndex + 2).addr
      
      # Se escoge el operador opuesto, para no seguir evaluando 
      # Con uno que no cumpla, la expresión completa es falsa
      if operator == "<":
        instruction = SingleInstruction(operator=LESS, arg1=operand1, arg2=operand2, result=temp)
      elif operator == ">":
        lessOrEqualTemp = self.newTemp(BoolType())
        instruction = SingleInstruction(operator=LESS_EQUAL, arg1=operand1, arg2=operand2, result=lessOrEqualTemp)
        instruction.concat(SingleInstruction(operator=NOT, arg1=lessOrEqualTemp, result=temp))
        
      elif operator == "<=":
        instruction = SingleInstruction(operator=LESS_EQUAL, arg1=operand1, arg2=operand2, result=temp)
      elif operator == ">=":
        lessTemp = self.newTemp(BoolType())
        instruction = SingleInstruction(operator=LESS, arg1=operand1, arg2=operand2, result=lessTemp)
        instruction.concat(SingleInstruction(operator=NOT, arg1=lessTemp, result=temp))
      else:
        raise NotImplementedError("exitComparison: Operador no implementado)")
      
      if code == None:
        code = instruction
      else:
        code.concat(instruction)
    
    # Guardar addr de resultado de operación de comparación y concatenar código
    ctx.addr = temp
    ctx.code.concat(code)

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
    
    # Son operaciones aritméticas
    
    code = None
    numOperations = (len(ctx.children) - 1) // 2
    nodeType = ctx.type
    
    firstOperand = ctx.getChild(0).addr
    
    for i in range(numOperations):
      
      operatorLexeme = ctx.getChild(i * 2 + 1).getText()
      secondOperand = ctx.getChild(i * 2 + 2).addr
      
      
      # Determinar token de operación
      if operatorLexeme == "+":
        operation = PLUS
        
        # Si el nodo es de tipo string, concatenar
        # Si es ambiguo, preferir suma aritmética
        if nodeType.strictEqualsType(StringType):
          operation = CONCAT
          
      elif operatorLexeme == "-":
        operation = MINUS
      else:
        raise NotImplementedError("exitTerm: Operador no implementado")
      
      if firstOperand.strictEqualsType(StringType) or secondOperand.strictEqualsType(StringType):
        # Si alguno de los operandos es string, concatenar
        tempType = StringType()
      elif firstOperand.strictEqualsType(IntType) and secondOperand.strictEqualsType(IntType):
        # Si ambos operandos son enteros, resultado es entero
        tempType = IntType()
      else:
        # Si uno es float o es ambiguo, resultado es float
        tempType = FloatType()
      
      temp = self.newTemp(tempType)
      
      # Agregar instrucción de operación
      instruction = SingleInstruction(result=temp, arg1=firstOperand, operator=operation, arg2=secondOperand)
      if code == None:
        code = instruction
      else:
        code.concat(instruction)
        
      # Actualizar primer operando con resultado de operación
      firstOperand = temp
      
    # Guardar addr de resultado de operación y concatenar código
    ctx.addr = firstOperand
    ctx.code.concat(code)  

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
    
    # Son operaciones aritméticas
    
    code = None
    numOperations = (len(ctx.children) - 1) // 2
    
    firstOperand = ctx.getChild(0).addr
    
    for i in range(numOperations):
      
      operatorLexeme = ctx.getChild(i * 2 + 1).getText()
      secondOperand = ctx.getChild(i * 2 + 2).addr
      
      
      # Determinar token de operación
      if operatorLexeme == "*":
        operation = MULTIPLY
      elif operatorLexeme == "/":
        operation = DIVIDE
      elif operatorLexeme == "%":
        operation = MOD
      else:
        raise NotImplementedError("exitFactor: Operador no implementado")
      
      
      if operatorLexeme == "/":
        tempType = FloatType()
      elif firstOperand.strictEqualsType(IntType) and secondOperand.strictEqualsType(IntType):
        tempType = IntType()
      else:
        tempType = FloatType()
      
      temp = self.newTemp(tempType)
      
      # Agregar instrucción de operación
      instruction = SingleInstruction(result=temp, arg1=firstOperand, operator=operation, arg2=secondOperand)
      if code == None:
        code = instruction
      else:
        code.concat(instruction)
        
      # Actualizar primer operando con resultado de operación
      firstOperand = temp
      
    # Guardar addr de resultado de operación y concatenar código
    ctx.addr = firstOperand
    ctx.code.concat(code)      
      

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
    
    instanceType = ctx.type
    
    # Crear en código intermedio el bloque de memoria para el objeto
    instanceAddr = self.newTemp() # Temp guarda dirección de inicio de objeto
    instanceCode = SingleInstruction(result=instanceAddr, arg1=MAX_PROPERTIES * MEM_ADDR_SIZE, operator=MALLOC)
    
    # Si tiene constructor, añadir código de constructor
    constructor = instanceType.getConstructor()
    if constructor != None:
      
      # Concatenar código necesario para otros parametros (hijos)
      instanceCode.concat(self.getChildrenCode(ctx))
      
      # Añadir parametro con dirección de memoria del objeto
      instanceCode.concat(SingleInstruction(operator=PARAM, arg1=instanceAddr))
      
      argsNumber = 1
      
      # Si hay argumentos
      if ctx.arguments() != None: 
        
        argsNumber += len(ctx.arguments().expression())
                
        # Añadir el resto de argumentos
        for argExpression in ctx.arguments().expression():
          # Agregar CI de argumentos
          instanceCode.concat(SingleInstruction(operator=PARAM, arg1=argExpression.addr))
      
      # Realizar llamada al constructor
      instanceCode.concat(SingleInstruction(operator=CALL, arg1=constructor, arg2=argsNumber, operatorFirst=True))
    
    ctx.code = instanceCode
    ctx.addr = instanceAddr

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
    
    operation = ctx.getChild(0).getText()
    operand = ctx.getChild(1).addr
    temp = self.newTemp(ctx.type)
    
    
    if operation == "-":
      # Operador unario negativo. 0 - X = -X
      ctx.code.concat(SingleInstruction(result=temp, arg1=Value(0, NumberType()), operator=MINUS, arg2=operand))

    else:
      # Operador unario not
      # 1 XOR 1 = 0, 0 XOR 1 = 1
      ctx.code.concat(SingleInstruction(result=temp, arg1=operand, operator=XOR, arg2=Value(1, NumberType())))
      
    ctx.addr = temp
    
  def enterCall(self, ctx: CompiscriptParser.CallContext):
    if not self.continueCodeGeneration(): return

  def exitCall(self, ctx: CompiscriptParser.CallContext, callAborted = False):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    
    # Si call fue abortada (sin errores críticos), no se genera código
    if callAborted:
      ctx.addr = None
      return
    
    # Si es solo un nodo, pasar addr
    if len(ctx.children) == 1:
      childNode = ctx.getChild(0)
      ctx.addr = childNode.addr
      return
    
    nodeType = None
    nodeAddr = None
    code = None
    functionCallsCode = None
    functionCall = False
    objectAddr = None # Guarda la dirección de memoria de un bloque de memoria de un objeto (this)

    for index, child in enumerate(ctx.getChildren()):     
      
      if isinstance(child, CompiscriptParser.PrimaryContext):
        # Obtener el addr del nodo primario (identificador)
        primary_context = ctx.primary()
        
        nodeAddr = primary_context.addr
        nodeType = primary_context.type

      elif isinstance(child, tree.Tree.TerminalNode):

        token = child.getSymbol()
        lexeme = child.getText()


        if lexeme == "(":
          # Es una llamada a función
          
          functionCall = True
          obtainedParams = 0 if ctx.arguments(0) == None else len(ctx.arguments(0).expression())
          functionDef = nodeType.getType()
          funCallCode = EmptyInstruction()
          
          numOfParams = obtainedParams
          
          # Si la función es una sobrecarga, obtener la función que corresponde a los argumentos
          if nodeType.strictEqualsType(FunctionOverload):
            functionDef = functionDef.getFunctionByParams(obtainedParams)
          
          # Si es un método, agregar como primer parametro la dirección de memoria del objeto
          if functionDef.isMethod:
            numOfParams += 1 # Tomar en cuenta param "this"
            if nodeType.strictEqualsType(SuperMethodWrapper):
              # Si es una llamada super.method, obtener referencia de objeto this
              currentParams = self.thisReferenceParams.getParams()
              thisTemp = currentParams.get("this")
              funCallCode.concat(SingleInstruction(operator=PARAM, arg1=thisTemp))
            
            else: # referencia normal
              funCallCode.concat(SingleInstruction(operator=PARAM, arg1=objectAddr))
              
          
          # Agregar CI de paso de argumentos
          if obtainedParams > 0:
            for argExpression in ctx.arguments(0).expression():
              funCallCode.concat(SingleInstruction(operator=PARAM, arg1=argExpression.addr))

          # Añadir Ci de llamada a función
          callInstr = SingleInstruction(operator=CALL, arg1=functionDef, arg2=numOfParams, operatorFirst=True)
          funCallCode.concat(callInstr)
          
          # Cuando se hace una llamada a una función, el código de acceso a propiedades anteriores
          # ya no es relevante, por lo que se limpia
          if functionCallsCode != None:
            code = functionCallsCode.copyInstructions()
            
          # Concatenar solo al código de las funciones
          if functionCallsCode == None:
            functionCallsCode = funCallCode
          else:
            functionCallsCode.concat(funCallCode)
          
          # Crear un nuevo temporal para guardar el valor de retorno
          returnType = functionDef.returnType.getType()
          returnTemp = self.newTemp(returnType)
          funCallCode.concat(SingleInstruction(result=returnTemp, arg1=RETURN_VAL))
          
          # Asignar valor de retorno como addr
          nodeAddr = returnTemp
          
          # Guardar tipo de retorno de la función
          nodeType = returnType

        elif lexeme == ".":
            # Se está accediendo a un atributo de un objeto
            functionCall = False
            objectAddr = nodeAddr
                        
            # Verificar si es un acceso a un atributo (no es una llamada a método)
            isProp = False
            propIdNode = ctx.getChild(index + 1)
            parenthesis = ctx.getChild(index + 2)
            
            propId = propIdNode.getText()
            
            isProp = propIdNode != None and (parenthesis == None or parenthesis.getText() != "(")
            
            if isProp:
              # Se hace referencia a una propiedad
              if nodeType.strictEqualsType(ClassSelfReferenceType):
                classDef = nodeType.getType().classType
                nodeType = classDef.getProperty(propId) # Devolver el tipo de la propiedad
                propertyIndex = classDef.getPropertyIndex(propId)
                
              elif nodeType.strictEqualsType(InstanceType):
                instance = nodeType.getType()
                nodeType = instance.getProperty(propId) # Devolver el tipo de la propiedad
                propertyIndex = instance.getPropertyIndex(propId)
                
              # Realizar offset relativo a la dirección de memoria del objeto
              propertyPosition = Offset(nodeAddr, propertyIndex * MEM_ADDR_SIZE)
              nodeAddr = propertyPosition
          
              
            else:
              # Se hace referencia a un método
              # Devolver el método(o sobrecarga) de la clase
              # No es necesario agregar CI, aqui solo se obtiene el tipo de la función
              
              if nodeType.strictEqualsType(ClassSelfReferenceType):
                classDef = nodeType.getType().classType
                nodeType = classDef.getMethod(propId) 
                
              elif nodeType.strictEqualsType(InstanceType):
                instance = nodeType.getType()
                nodeType = instance.getMethod(propId)
                
            

        elif lexeme == "[":

          # Se está accediendo a un elemento de un array
          
          functionCall = False
          
          arrayBase = nodeType
          
          indexToken = ctx.expression(0)
          
          # Calcular el desplazamiento: indice * tamaño de casilla
          arrayShiftTemp = self.newTemp()
          arrayInstr = SingleInstruction(result=arrayShiftTemp, arg1=indexToken.addr, arg2=MEM_ADDR_SIZE, operator=MULTIPLY)
          
          if code == None:
            code = arrayInstr
          else:
            code.concat(arrayInstr)
          
          # Asignar array[arrayShift] a addr
          arrayElement = Offset(arrayBase, arrayShiftTemp)
                
          nodeAddr = arrayElement
          nodeType = AnyType()
          
    ctx.addr = nodeAddr # Guardar dirección de memoria de último elemento  

    # Si call termina siendo una llamada, solo agregar CI de llamadas
    if functionCall:
      ctx.code.concat(functionCallsCode)
    else:
      # Si no es una llamada, agregar CI de acceso a atributos y elem. de array
      ctx.code.concat(code)


  def enterPrimary(self, ctx: CompiscriptParser.PrimaryContext):
    if not self.continueCodeGeneration(): return

  def exitPrimary(self, ctx: CompiscriptParser.PrimaryContext):
    if not self.continueCodeGeneration(): return
    ctx.code = self.getChildrenCode(ctx)
    nodeType = ctx.type
    
    if len(ctx.children) == 1:
      # Un solo nodo hijo
      lexeme = ctx.getChild(0).getText()
      
      if not isinstance(ctx.getChild(0), tree.Tree.TerminalNode):
        # Es un no terminal
        ctx.addr = ctx.getChild(0).addr

      elif isinstance(nodeType,(NumberType, StringType)):
        
        # Crear un nuevo temporal con valor
        temp = self.newTemp(ctx.type)
        # Guardar asignación en CI
        ctx.code.concat(SingleInstruction(result=temp, arg1=Value(lexeme, nodeType)))
        ctx.addr = temp
        
      elif isinstance(nodeType, NilType):
        temp = self.newTemp(ctx.type)
        ctx.code.concat(SingleInstruction(result=temp, arg1=Value(None, NilType())))
        ctx.addr = temp
        
      elif isinstance(nodeType, BoolType):
        temp = self.newTemp(ctx.type)
        
        val = trueValue if lexeme == "true" else falseValue
        ctx.code.concat(SingleInstruction(result=temp, arg1=val))
        ctx.addr = temp
      
      elif isinstance(nodeType, (ObjectType, FunctionType,FunctionOverload, ClassType)):
        ctx.addr = nodeType
        
      elif lexeme == "this":
        
        # Obtener referencia a this
        currentParams = self.thisReferenceParams.getParams()
        thisTemp = currentParams.get("this")
        
        ctx.addr = thisTemp
        
      
    elif ctx.expression() != None:
      # Expresión en paréntesis
      ctx.addr = ctx.expression().addr
      
    elif nodeType.strictEqualsType(SuperMethodWrapper):
      # Se está pasando un método de clase padre (super.method)
      ctx.addr = nodeType
    
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
