from antlr4 import *
from antlr.CompiscriptListener import CompiscriptListener
from antlr.CompiscriptParser import CompiscriptParser
from SymbolTable import SymbolTable, FunctionType, ScopeType, AnyType, NumberType, StringType, BoolType, NilType, UnionType, ArrayType, InstanceType, TypesNames, FunctionOverload, ClassSelfReferenceType
from Errors import SemanticError, CompilerError
from ParamsTree import ParamsTree
from IntermediateCodeGenerator import IntermediateCodeGenerator
class SemanticChecker(CompiscriptListener):
    
    def __init__(self) -> None:
      super().__init__()

      self.symbolTable = SymbolTable()
      self.errors = []
      self.params = ParamsTree()
      self.intermediateCodeGenerator = IntermediateCodeGenerator(self.symbolTable, self.errors)

    def addSemanticError(self, error):
      self.errors.append(error)


    def enterProgram(self, ctx: CompiscriptParser.ProgramContext):
      super().enterProgram(ctx)
      self.params.initNodeParams() # Inicializar el árbol de parámetros


    def exitProgram(self, ctx: CompiscriptParser.ProgramContext):
      super().exitProgram(ctx)
      print(self.symbolTable.str())


    def enterDeclaration(self, ctx: CompiscriptParser.DeclarationContext):
      return super().enterDeclaration(ctx)
    

    def exitDeclaration(self, ctx: CompiscriptParser.DeclarationContext):
      return super().exitDeclaration(ctx)


    def enterClassDecl(self, ctx: CompiscriptParser.ClassDeclContext):
        
        """
        Guarda una nueva clase en el scope actual, creando y cambiando al scope del cuerpo de la 
        clase. Si la clase tiene una clase padre, verifica que exista en la tabla de símbolos.
        """
        super().enterClassDecl(ctx)

        # Obtener el nombre de la clase y clase heredada
        identifiers = [child for child in ctx.children 
                        if isinstance(child, tree.Tree.TerminalNodeImpl)  # type: ignore
                        and child.symbol.type == CompiscriptParser.IDENTIFIER]
          
        classToken = identifiers[0].getSymbol()
        className = classToken.text

        # Obtener clase heredada
        parentClassNode = None
        parentClassDef = None
        if len(identifiers) > 1:
          parentClassNode = identifiers[1]

          # Verificar si la clase heredada existe
          parentClassDef = self.symbolTable.currentScope.searchClass(parentClassNode.getText())
          if parentClassDef == None:
            # error semántico
            parentClassToken = parentClassNode.getSymbol()
            error = SemanticError(f"La clase {parentClassNode.getText()} no existe", parentClassToken.line, parentClassToken.column)
            self.addSemanticError(error)
            

        # Crear scope para la clase
        classScope = self.symbolTable.createScope(ScopeType.CLASS)
        
        # Verificar si el nombre de la clase ya ha sido declarado (solo en el scope actual)
        if self.symbolTable.currentScope.searchElement(className, searchInParentScopes=False, searchInParentClasses=False):
          # error semántico
          error = SemanticError(f"El identificador '{className}' ya ha sido declarado.", classToken.line, classToken.column)
          self.addSemanticError(error)
          ctx.type = error
        else:
          self.symbolTable.addClassToCurrentScope(className, classScope, parentClassDef)

        # Cambiar al scope de la clase
        self.symbolTable.setScope(classScope)


    def exitClassDecl(self, ctx: CompiscriptParser.ClassDeclContext):
      """
      Salir del scope de la clase
      """
      super().exitClassDecl(ctx)

      # Volver al scope padre
      self.symbolTable.returnToParentScope()


    def enterFunDecl(self, ctx: CompiscriptParser.FunDeclContext):
      return super().enterFunDecl(ctx)
    

    def exitFunDecl(self, ctx: CompiscriptParser.FunDeclContext):
      return super().exitFunDecl(ctx)
    

    def enterVarDecl(self, ctx: CompiscriptParser.VarDeclContext):
      return super().enterVarDecl(ctx)
    

    def exitVarDecl(self, ctx: CompiscriptParser.VarDeclContext):

      """
      Declaración de variables
      """
      super().exitVarDecl(ctx)

      # Validar que el nombre de la variable no sea un erro léxico
      if isinstance(ctx.IDENTIFIER(), tree.Tree.ErrorNodeImpl): # type: ignore
        return # Saltar validaciones semánticas de asignación de variable
      
      # Obtener nombre de variable
      identifierToken = ctx.IDENTIFIER().getSymbol()
      identifierName = identifierToken.text

      # Verificar si la variable ya ha sido declarada (exclusivamente en dicho scope)
      if self.symbolTable.currentScope.searchElement(identifierName, searchInParentScopes=False, searchInParentClasses=False):
        # error semántico
        error = SemanticError(f"El identificador '{identifierName}' ya ha sido declarado.", identifierToken.line, identifierToken.column)
        self.addSemanticError(error)
        ctx.type = error
        return
      
      # Obtener tipo de la variable
      varType = None
      if ctx.expression() != None:
        varType = ctx.expression().type
      else:
        varType = NilType()

      # Agregar variable al scope actual
      self.symbolTable.currentScope.addObject(identifierName, varType)


    def enterStatement(self, ctx: CompiscriptParser.StatementContext):
      return super().enterStatement(ctx)
    

    def exitStatement(self, ctx: CompiscriptParser.StatementContext):
      return super().exitStatement(ctx)


    def enterBreakStmt(self, ctx: CompiscriptParser.BreakStmtContext):
      super().enterBreakStmt(ctx)

      # Verificar que el break esté dentro de un loop
      if not self.symbolTable.currentScope.isInsideLoop():
        # error semántico
        line = ctx.start.line
        column = ctx.start.column
        error = SemanticError("La sentencia 'break' solo puede ser usada dentro de un loop.", line, column)
        self.addSemanticError(error)
        ctx.type = error
    

    def exitBreakStmt(self, ctx: CompiscriptParser.BreakStmtContext):
      return super().exitBreakStmt(ctx)
    

    def enterContinueStmt(self, ctx: CompiscriptParser.ContinueStmtContext):
      super().enterContinueStmt(ctx)

      # Verificar que el continue esté dentro de un loop
      if not self.symbolTable.currentScope.isInsideLoop():
        # error semántico
        line = ctx.start.line
        column = ctx.start.column
        error = SemanticError("La sentencia 'continue' solo puede ser usada dentro de un loop.", line, column)
        self.addSemanticError(error)
        ctx.type = error
    

    def exitContinueStmt(self, ctx: CompiscriptParser.ContinueStmtContext):
      return super().exitContinueStmt(ctx)
    

    def enterExprStmt(self, ctx: CompiscriptParser.ExprStmtContext):
      return super().enterExprStmt(ctx)


    def exitExprStmt(self, ctx: CompiscriptParser.ExprStmtContext):
      super().exitExprStmt(ctx)

      # Asignar tipo de nodo hijo
      ctx.type = ctx.expression().type


    def enterForStmt(self, ctx: CompiscriptParser.ForStmtContext):
      super().enterForStmt(ctx)

      _, nodeParams = self.params.initNodeParams()

      # Indicar que el siguiente bloque es un loop en parametros
      nodeParams.add("blockType", ScopeType.LOOP) 


    def exitForStmt(self, ctx: CompiscriptParser.ForStmtContext):
      super().exitForStmt(ctx)

      self.params.removeNodeParams()

      section = 0 # 0: primera expresión, 1: segunda expresión, 2: tercera expresión

      # Verificar que segunda expresión sea de tipo booleano
      for child in ctx.children:
        if isinstance(child, CompiscriptParser.ExpressionContext) and section == 1:

          if child.type.equalsType(CompilerError):
            # Si el tipo de la expresión es un error, ignorar
            return

          if not child.type.equalsType(BoolType):
            # error semántico, la condición no es de tipo booleano o any
            line = child.start.line
            column = child.start.column
            error = SemanticError("La condición del for debe ser de tipo booleano.", line, column)
            self.addSemanticError(error)
            return
        elif child.getText() == ";" or isinstance(child, CompiscriptParser.VarDeclContext) or \
              isinstance(child, CompiscriptParser.ExprStmtContext):
          
          # Cambiar de sección del for
          section += 1


    def enterIfStmt(self, ctx: CompiscriptParser.IfStmtContext):
      super().enterIfStmt(ctx)

      _, nodeParams = self.params.initNodeParams()

      # Indicar que el siguiente bloque es un bloque condicional en parametros
      nodeParams.add("blockType", ScopeType.CONDITIONAL) 


    def exitIfStmt(self, ctx: CompiscriptParser.IfStmtContext):
      super().exitIfStmt(ctx)

      self.params.removeNodeParams()


      # Verificar que la condición sea de tipo booleano
      condition = ctx.expression()
      if condition != None: # Si es none, es un error léxico o sintactico, ignorar
        
        if not condition.type.equalsType((BoolType, CompilerError)):
          # error semántico, la condición no es de tipo booleano o any
          line = condition.start.line
          column = condition.start.column
          error = SemanticError("La condición del if debe ser de tipo booleano.", line, column)
          self.addSemanticError(error)
          return


    def enterPrintStmt(self, ctx: CompiscriptParser.PrintStmtContext):
      return super().enterPrintStmt(ctx)
    

    def exitPrintStmt(self, ctx: CompiscriptParser.PrintStmtContext):
      super().exitPrintStmt(ctx)

      expression = ctx.expression()

      if expression != None:
        print("\033[32mPRINT:\033[0m", expression.type)


    def enterReturnStmt(self, ctx: CompiscriptParser.ReturnStmtContext):
      return super().enterReturnStmt(ctx)
    

    def exitReturnStmt(self, ctx: CompiscriptParser.ReturnStmtContext):
      super().exitReturnStmt(ctx)

      # Objeto FunctionType que corresponde al scope función que contiene la sentencia 'return'
      functionDef = self.symbolTable.currentScope.getParentFunction()

      if functionDef == None:
        # error semántico
        line = ctx.start.line
        column = ctx.start.column
        error = SemanticError("La sentencia 'return' solo puede ser usada dentro de una función.", line, column)
        self.addSemanticError(error)
        ctx.type = error
        return
      
      # Obtener tipo de retorno de la función
      # Si no tiene tipo de retorno, se asume que es nil
      expression = ctx.expression()

      if expression == None:
        functionDef.setReturnType(NilType())
        return
      
      # Verificar si la ubicación de ejecución es ambigua (el return podría o no ejecutarse)
      # Busca hasta encontrar el scope de la función que contiene la sentencia 'return'
      isAmbiguous = self.symbolTable.currentScope.isExecutionAmbiguous(functionDef)
      
      # Obtener tipo de la expresión y asignar al tipo de retorno
      if not functionDef.returnTypeHasChanged:
        # Si el tipo de retorno no ha sido definido, asignar el tipo de la expresión
        # Si la ejecución del return no es ambigua, evitar que el tipo de dato sea sobrescrito
        functionDef.setReturnType(expression.type, preventOverwrite= not isAmbiguous)
      else:
        # Ya se ha definido un tipo de retorno
        # Si no es igual, hacer una unión de tipos
        if functionDef.returnType != expression.type:
          unionType = UnionType(functionDef.returnType, expression.type)
          functionDef.setReturnType(unionType)


    def enterWhileStmt(self, ctx: CompiscriptParser.WhileStmtContext):
      super().enterWhileStmt(ctx)

      _, nodeParams = self.params.initNodeParams()

      # Indicar que el siguiente bloque es un loop en parametros
      nodeParams.add("blockType", ScopeType.LOOP) 


    def exitWhileStmt(self, ctx: CompiscriptParser.WhileStmtContext):
      super().exitWhileStmt(ctx)

      self.params.removeNodeParams()

      # Verificar que la condición sea de tipo booleano
      condition = ctx.expression()
      if condition != None: # Si es none, es un error léxico o sintactico, ignorar
        
        if not condition.type.equalsType((BoolType, CompilerError)):
          # error semántico, la condición no es de tipo booleano o any
          line = condition.start.line
          column = condition.start.column
          error = SemanticError("La condición del while debe ser de tipo booleano.", line, column)
          self.addSemanticError(error)
          return


    def enterBlock(self, ctx: CompiscriptParser.BlockContext):
      """
      Crear un nuevo scope para el bloque y cambiar al scope del bloque
      Si es un bloque de una función, agregar los parámetros al scope del bloque
      """
      super().enterBlock(ctx)

      parentParams, _ = self.params.initNodeParams()

      # Tipo de bloque, especificado en definición previa de fun, loop o if
      blockType = parentParams.get("blockType") # Obtenida de parametros proveidos de nodo superior
      blockScope = self.symbolTable.createScope(blockType)

      # Intenta obtener la referencia a una función de parametros proveidos por nodo superior
      # Si es asi, se le asigna el scope del bloque a la definición de la función
      functionDef = parentParams.get("reference")      

      if functionDef != None and functionDef.bodyScope == None:
        
        # Agregar params al scope de la función
        for param in functionDef.params:
          blockScope.addObject(param, AnyType())

        # Guardar el scope del bloque en la definición de la función
        functionDef.setBodyScope(blockScope)

      # Cambiar al scope del bloque
      self.symbolTable.setScope(blockScope)


    def exitBlock(self, ctx: CompiscriptParser.BlockContext):
      """
      Salir del scope del bloque
      """
      super().exitBlock(ctx)

      self.params.removeNodeParams()

      # Si existen copias locales de objetos o params heredados
      objectInheritances = self.symbolTable.currentScope.getInheritedObjectsList()
      propsInheritances = self.symbolTable.currentScope.getInheritedPropertiesList()
      for objectRef in objectInheritances + propsInheritances:

        if objectRef.reference == None:
          continue
        
        # Verificar si la ejecución es ambigua
        isAmbiguous = self.symbolTable.currentScope.isExecutionAmbiguous(objectRef.reference)

        if isAmbiguous:
          # Si la ejecución es ambigua, hacer una union de tipos
          previousType = objectRef.reference.getType()

          if previousType == None:
            # Si no tiene tipo previo, asignar nil
            previousType = NilType()

          unionType = UnionType(previousType, objectRef.getType())
          objectRef.reference.setType(unionType) # Asignar al padre la union
        
        else:
          # Si no es ambigua, sobrescribir el tipo
          objectRef.reference.setType(objectRef.getType())



      # Volver al scope padre
      self.symbolTable.returnToParentScope()


    def enterFunAnon(self, ctx: CompiscriptParser.FunAnonContext):
      super().enterFunAnon(ctx)

      _, nodeParams = self.params.initNodeParams()

      # Crear y agregar una función anonima
      functionDef = self.symbolTable.currentScope.addAnonymousFunction()

      # Indicar que el siguiente bloque es una función en parametros
      nodeParams.add("blockType", ScopeType.FUNCTION) 
      # Pasar como parametro la función
      nodeParams.add("reference", functionDef)
      


    def exitFunAnon(self, ctx: CompiscriptParser.FunAnonContext):
      super().exitFunAnon(ctx)

      self.params.removeNodeParams()

      # Retornar el tipo de la función (última creada) y eliminar de la tabla de símbolos
      functionDef = self.symbolTable.currentScope.popLastFunction()
      ctx.type = functionDef.getType()


    def enterExpression(self, ctx: CompiscriptParser.ExpressionContext):
      return super().enterExpression(ctx)
    

    def exitExpression(self, ctx: CompiscriptParser.ExpressionContext):
      super().exitExpression(ctx)

      # Asignar tipo de nodo hijo
      ctx.type = ctx.getChild(0).type


    def enterAssignment(self, ctx: CompiscriptParser.AssignmentContext):
      return super().enterAssignment(ctx)
    

    def exitAssignment(self, ctx: CompiscriptParser.AssignmentContext):
      super().exitAssignment(ctx)

      ctx.type = None

      if ctx.children == None:
        # No se proporcionó un valor para la asignación
        return

      if len(ctx.children) == 1:
        # Solo es un nodo primario
        ctx.type = ctx.logic_or().type if ctx.logic_or() != None else None
        return
      
      if ctx.assignment() == None:
        # No es una asignación
        return
      
      assignmentValueType = ctx.assignment().type.getType() # valor a asignar (su tipo)
      identifier = ctx.IDENTIFIER().getText() # identificador del atributo o variable

      if ctx.call() != None:
        # Es una asignación a un atributo de clase

        # receiver = parte izq de: receiver.method_or_property()
        # Si receiver fuera una variable, se obtendría el tipo de la variable
        receiverType = ctx.call().type.getType() 

        if receiverType.equalsType(CompilerError):
          # Si receiver es un error, solo ignorar
          ctx.type = receiverType
          return
        
        # Validar que el receiver sea un objeto de una clase o una self-reference "this"
        if not receiverType.equalsType(InstanceType) and not receiverType.equalsType(ClassSelfReferenceType):
          # error semántico
          line = ctx.start.line
          column = ctx.start.column
          error = SemanticError("Solo se pueden asignar atributos a objetos de una clase.", line, column)
          ctx.type = error
          self.addSemanticError(error)
          return

        # Se guarda el atributo aunque siempre es any
        
        if receiverType.strictEqualsType(InstanceType):
          # Si es una instancia, se agrega el atributo al objeto
          
          if assignmentValueType.strictEqualsType(FunctionType):
            # Si el valor a asignar es una función, se agrega como método
            receiverType.addMethod(identifier, assignmentValueType)
          else:
            # Si es cualquier otro tipo, se agrega como propiedad
            receiverType.addProperty(identifier)
          
        else:
          # Si es una referencia a la clase, se guarda en la definición de la clase
          classRef = receiverType.classType
          if assignmentValueType.strictEqualsType(FunctionType):
            # Si el valor a asignar es una función, se agrega como método
            classRef.addMethod(identifier, assignmentValueType)
          else:
            # Si es cualquier otro tipo, se agrega como propiedad
            classRef.addProperty(identifier)
          
        
      
      else:
        # Es una asignación a variable ya declarada


        assignmentValueType = ctx.assignment().type
        identifier = ctx.IDENTIFIER().getText() # identificador del atributo o variable
        
        
        assignmentValueType = ctx.assignment().type
        identifier = ctx.IDENTIFIER().getText() # identificador del atributo o variable
        
        # Obtener primero objeto solo en el scope actual
        paramRef = self.symbolTable.currentScope.getObject(identifier, searchInParentScopes=False)
        isLocal = paramRef != None

        if not isLocal:
          # Buscar en scopes padres
          paramRef = self.symbolTable.currentScope.getObject(identifier, searchInParentScopes=True)

        # Verificar si el identificador existe en el scope actual
        if paramRef == None:
          # error semántico
          line = ctx.start.line
          column = ctx.start.column
          error = SemanticError(f"El identificador '{identifier}' no ha sido declarado.", line, column)
          ctx.type = error
          self.addSemanticError(error)
          return
        
        # Actualizar el tipo de la variable
        if not isLocal:
          # Si no es local, se crea (o modifica) una copia local del objeto heredado
          self.symbolTable.currentScope.modifyInheritedObjectType(paramRef, assignmentValueType)
          
        else:
          # Si es local, se modifica el objeto local

          paramRef.setType(assignmentValueType)

        ctx.type = assignmentValueType

    def enterLogic_or(self, ctx: CompiscriptParser.Logic_orContext):
      return super().enterLogic_or(ctx)
    

    def exitLogic_or(self, ctx: CompiscriptParser.Logic_orContext):
      super().exitLogic_or(ctx)

      if len(ctx.children) <= 1:
        # Si solo hay un hijo, obtener y asignar su tipo
        child1 = ctx.logic_and(0)
        ctx.type = child1.type if child1 else None
        return
      
      ctx.type = BoolType() # Tipo bool por defecto

      # Si hay más de un nodo, verificar que todos sean numéricos
      for child in ctx.getChildren():
        if not isinstance(child, tree.Tree.TerminalNode): # type: ignore

          childType = child.type
          
          if childType.equalsType(CompilerError):
            # Si uno de los tipos es un error, solo ignorar
            ctx.type = childType
          
          elif not childType.equalsType(BoolType):
            # error semántico. Alguno de los factores no es numérico
            line = ctx.start.line
            column = ctx.start.column
            error = SemanticError("Los operandos en una sentencia 'or' debe ser de tipo bool.", line, column)
            self.addSemanticError(error)
            ctx.type = error


    def enterLogic_and(self, ctx: CompiscriptParser.Logic_andContext):
      return super().enterLogic_and(ctx)
    

    def exitLogic_and(self, ctx: CompiscriptParser.Logic_andContext):
      super().exitLogic_and(ctx)
      
      if len(ctx.children) <= 1:
        # Si solo hay un hijo, obtener y asignar su tipo
        child1 = ctx.equality(0)
        ctx.type = child1.type if child1 else None
        return
      
      ctx.type = BoolType() # Tipo bool por defecto

      # Si hay más de un nodo, verificar que todos sean numéricos
      for child in ctx.getChildren():
        if not isinstance(child, tree.Tree.TerminalNode): # type: ignore

          childType = child.type
          
          if childType.equalsType(CompilerError):
            # Si uno de los tipos es un error, solo ignorar
            ctx.type = childType
          
          elif not childType.equalsType(BoolType):
            # error semántico. Alguno de los factores no es numérico
            line = ctx.start.line
            column = ctx.start.column
            error = SemanticError("Los operandos en una sentencia 'and' debe ser de tipo bool.", line, column)
            self.addSemanticError(error)
            ctx.type = error


    def enterEquality(self, ctx: CompiscriptParser.EqualityContext):
      return super().enterEquality(ctx)


    def exitEquality(self, ctx: CompiscriptParser.EqualityContext):
      super().exitEquality(ctx)

      if len(ctx.children) <= 1:
        # Si solo hay un hijo, obtener el tipo y asignar al nodo
        child1 = ctx.comparison(0)
        ctx.type = child1.type if child1 else None
        return

      # Si hay más de un hijo, verificar que todos sean del mismo tipo

      type = None

      for child in ctx.getChildren():
        if not isinstance(child, tree.Tree.TerminalNode): # type: ignore

          childType = child.type

          if (type != None and type.equalsType(CompilerError)):
            # Si uno de los tipos es un error, solo ignorar
            ctx.type = type
            return
          
          if childType.equalsType(CompilerError):
            # Si uno de los tipos es un error, solo ignorar
            ctx.type = childType
            return

          if type != None and not type.equalsType(childType.__class__):
            # error semántico. Los tipos no son comparables
            line = ctx.start.line
            column = ctx.start.column
            error = SemanticError(f"Los tipos '{type.name}' y '{childType.name}' no son comparables.", line, column)
            self.addSemanticError(error)
            ctx.type = error
            return
          
          type = childType

      ctx.type = BoolType()


    def enterComparison(self, ctx: CompiscriptParser.ComparisonContext):
      return super().enterComparison(ctx)


    def exitComparison(self, ctx: CompiscriptParser.ComparisonContext):
      super().exitComparison(ctx)

      if len(ctx.children) <= 1:
        # Si solo hay un hijo, obtener el tipo y asignar al nodo
        child1 = ctx.term(0)
        ctx.type = child1.type if child1 else None
        return

      # Si hay más de un hijo, verificar que todos sean del mismo tipo

      type = None

      for child in ctx.getChildren():
        if not isinstance(child, tree.Tree.TerminalNode): # type: ignore

          childType = child.type

          if type != None and type.equalsType(CompilerError):
            # Si uno de los tipos es un error, solo ignorar
            ctx.type = type
            return
          
          if childType.equalsType(CompilerError):
            # Si uno de los tipos es un error, solo ignorar
            ctx.type = childType
            return
          
          if type != None  and not type.equalsType(childType.__class__):
            # error semántico. Los tipos no son comparables
            line = child.start.line
            column = child.start.column
            error = SemanticError(f"Los tipos '{type.name}' y '{childType.name}' no son comparables.", line, column)
            self.addSemanticError(error)
            ctx.type = error
            return
          
          type = childType

      ctx.type = BoolType()


    def enterTerm(self, ctx: CompiscriptParser.TermContext):
      return super().enterTerm(ctx)


    def exitTerm(self, ctx: CompiscriptParser.TermContext):
      super().exitTerm(ctx)

      # Si solo hay un nodo, obtener tipo y asignar al nodo
      if len(ctx.children) <= 1:
        child1 = ctx.factor(0)
        ctx.type = child1.type if child1 else None
        return

      # Si hay más de un factor, verificar tipos
      
      operator = ctx.getChild(1).getText() # Operador inicial (+ | -)
        
      childTypes = [] # Va a almacenar tuplas con los tipos que puede adoptar cada nodo (number o string y number)      
      hasErrors = False
      
      for child in ctx.getChildren():
        
        validTypes = (NumberType, StringType) if operator == "+" else (NumberType,)
        typesNames = (TypesNames.NUMBER.value, TypesNames.STRING.value) if operator == "+" else (TypesNames.NUMBER.value,)
    
        if not isinstance(child, tree.Tree.TerminalNode): # type: ignore # terminales (+ | -)

          childType = child.type
          
          if childType.equalsType(CompilerError):
            # Si uno de los tipos es un error, solo ignorar
            ctx.type = childType
            hasErrors = True
          
          elif not childType.equalsType(validTypes):
            # error semántico. Alguno de los factores no es numérico
            line = child.start.line
            column = child.start.column
            error = SemanticError(f"El factor debe ser de tipo {' o '.join(typesNames)}.", line, column)
            self.addSemanticError(error)
            ctx.type = error
            hasErrors = True
          
          else:
            
            # Determinar que tipo es el compatible (o si son ambos)
            if childType.strictEqualsType(NumberType):
              childTypes.append(NumberType)
            elif childType.strictEqualsType(StringType):
              childTypes.append(StringType)
            else:
              childTypes.append(AnyType)
        
        else:
          operator = child.getText() # Cambiar operador
          
      if not hasErrors:
        
        # Inferir tipo: Si hay un string estricto, todo es string
        # Si hay un any y no hay strings, puede ser ambos tipos
        # si solo hay numbers, el resultado es number
        
        if StringType in childTypes:
          ctx.type = StringType()
        elif AnyType in childTypes:
          ctx.type = UnionType(NumberType(), StringType())
        else:
          ctx.type = NumberType()


    def enterFactor(self, ctx: CompiscriptParser.FactorContext):
      return super().enterFactor(ctx)


    def exitFactor(self, ctx: CompiscriptParser.FactorContext):
      super().exitFactor(ctx)
      
      # Si solo hay un nodo, retornar su tipo
      if len(ctx.children) <= 1:
        child1 = ctx.unary(0)
        ctx.type = child1.type if child1 else None
        return

      # Si hay más de un factor, verificar que todos sean numéricos
      
      ctx.type = NumberType() # Tipo numérico por defecto (puede cambiar a error)

      for child in ctx.getChildren():
        if not isinstance(child, tree.Tree.TerminalNode): # type: ignore

          childType = child.type
          
          if childType.equalsType(CompilerError):
            # Si uno de los tipos es un error, solo ignorar
            ctx.type = childType
          
          elif not childType.equalsType(NumberType):
            # error semántico. Alguno de los factores no es numérico
            line = child.start.line
            column = child.start.column
            error = SemanticError("El factor debe ser de tipo numérico.", line, column)
            self.addSemanticError(error)
            ctx.type = error


    def enterArray(self, ctx: CompiscriptParser.ArrayContext):
      return super().enterArray(ctx)
    

    def exitArray(self, ctx: CompiscriptParser.ArrayContext):
      super().exitArray(ctx)

      # Crear tipo array de tipos any
      ctx.type = ArrayType()


    def enterInstantiation(self, ctx: CompiscriptParser.InstantiationContext):
      return super().enterInstantiation(ctx)
    

    def exitInstantiation(self, ctx: CompiscriptParser.InstantiationContext):
      super().exitInstantiation(ctx)

      # Obtener el tipo de la clase a instanciar
      classNameToken = ctx.IDENTIFIER()

      if classNameToken == None: # Error léxico o sintáctico, ignorar
        ctx.type = None
        return
      
      className = classNameToken.getText()

      # Verificar si la clase existe
      classDef = self.symbolTable.currentScope.searchClass(className)
      line = ctx.start.line
      column = ctx.start.column

      if classDef == None:
        # error semántico 
        error = SemanticError(f"La clase {className} no ha sido definida.", line, column)
        self.addSemanticError(error)
        ctx.type = error
        return
      
      # Verificar si el número de parametros del constructor es correcto
      obtainedParams = 0 if ctx.arguments() == None else len(ctx.arguments().expression())
      if classDef.constructor != None and (obtainedParams != len(classDef.constructor.params)):
        # error semántico, número incorrecto de parámetros
        expectedParams = len(classDef.constructor.params)
        error = SemanticError(f"El constructor de la clase '{className}' espera {expectedParams} parámetros pero se obtuvo {obtainedParams}.", line, column)
        self.addSemanticError(error)
        ctx.type = error
        return
      elif classDef.constructor == None and obtainedParams != 0:
        # error semántico, la clase no espera argumentos en el constructor (no existe constructor)
        error = SemanticError(f"La clase '{className}' no espera argumentos en el constructor.", line, column)
        self.addSemanticError(error)
        ctx.type = error
        return
      
      # Crear una instancia de la clase
      instanceDef = InstanceType(classDef)
      ctx.type = instanceDef


    def enterUnary(self, ctx: CompiscriptParser.UnaryContext):
      return super().enterUnary(ctx)
    

    def exitUnary(self, ctx: CompiscriptParser.UnaryContext):
      super().exitUnary(ctx)

      # Si solo hay un nodo hijo, asignar su tipo al nodo
      if len(ctx.children) <= 1:
        child1 = ctx.call()
        ctx.type = child1.type if child1 else None
        return

      operator = ctx.getChild(0).getText()
      childType = ctx.unary().type

      if childType.equalsType(CompilerError):
        # Si el tipo del hijo es un error, asignar el error al nodo
        ctx.type = childType
        return
      
      if operator == "-" and not childType.equalsType(NumberType):
        # error semántico. El operador unario '-' solo puede ser usado con números
        line = ctx.start.line
        column = ctx.start.column
        error = SemanticError("El operador unario '-' solo puede ser usado con números.", line, column)
        self.addSemanticError(error)
        ctx.type = error
        return
      
      if operator == "!" and not childType.equalsType(BoolType):
        # error semántico. El operador unario '!' solo puede ser usado con booleanos
        line = ctx.start.line
        column = ctx.start.column
        error = SemanticError("El operador unario '!' solo puede ser usado con booleanos.", line, column)
        self.addSemanticError(error)
        ctx.type = error
        return
      
      ctx.type = childType # Asignar el tipo del hijo al nodo

    def enterCall(self, ctx: CompiscriptParser.CallContext):
      return super().enterCall(ctx)
    

    def exitCall(self, ctx: CompiscriptParser.CallContext):
      super().exitCall(ctx)

      primary_name = None
      node_type = None

      for index, child in enumerate(ctx.getChildren()):     
        
        if isinstance(child, CompiscriptParser.PrimaryContext):
          # Obtener el tipo del nodo primario (identificador)
          primary_context = ctx.primary()

          node_type = primary_context.type
          primary_name = child.getText()

        elif isinstance(child, tree.Tree.TerminalNode): # type: ignore

          token = child.getSymbol()
          lexeme = child.getText()
          line = token.line
          column = token.column 

          if lexeme == "(":

            # Verificar si es una llamada a función
            if not node_type.equalsType(CompilerError) and not node_type.equalsType(FunctionType):

              # Error semántico, se está llamando a algo diferente a una función
              error = SemanticError(f"El identificador '{primary_name}' no es una función.", line, column)
              self.addSemanticError(error)
              ctx.type = error
              break
            elif node_type.strictEqualsType(FunctionType) or node_type.strictEqualsType(FunctionOverload) :
              
              obtainedParams = 0 if ctx.arguments(0) == None else len(ctx.arguments(0).expression())
              
              functionDef = node_type
              
              # Si la función es una sobrecarga, obtener la función que corresponde a los argumentos
              if node_type.strictEqualsType(FunctionOverload):
                functionDef = node_type.getFunctionByParams(obtainedParams)

              # Obtener el tipo de retorno de la función (solo si es exclusivamente una función)
              # Si es any, se mantiene el tipo any
              node_type = functionDef.returnType

              # Si es estrictamente una función, se verifica el número de params
  
              if obtainedParams != len(functionDef.params):
                # error semántico, número incorrecto de parámetros
                expectedParams = len(functionDef.params)
                error = SemanticError(f"La función '{primary_name}' espera {expectedParams} parámetros pero se obtuvo {obtainedParams}.", line, column)
                self.addSemanticError(error)
                node_type = error
                break


          elif lexeme == ".":
            # Se está accediendo a un atributo de un objeto

            if node_type.equalsType(CompilerError):
              break

            # Verificar si el identificador es null
            if node_type.strictEqualsType(NilType):
              # error semántico
              error = SemanticError("No se puede acceder a un atributo de un objeto nulo.", line, column)
              self.addSemanticError(error)
              node_type = error
              break
            
            # Validar que el tipo sea un objeto o una referencia "this"
            if not node_type.equalsType(InstanceType) and not node_type.equalsType(ClassSelfReferenceType):
              # error semántico
              error = SemanticError(f"El identificador '{primary_name}' no es un objeto.", line, column)
              self.addSemanticError(error)
              node_type = error
              break
            
            # Verificar si es un acceso a un atributo (no es una llamada a método)
            isProp = False
            propId = ctx.getChild(index + 1)
            parenthesis = ctx.getChild(index + 2)
            
            isProp = propId != None and (parenthesis == None or parenthesis.getText() != "(")
            
            if isProp and node_type.strictEqualsType(ClassSelfReferenceType):
          
              # Guardar registro que se accedió a esa prop en la clase (this.algo)
              classDef = node_type.classType
              classDef.addProperty(propId.getText())
              
            elif isProp and node_type.strictEqualsType(InstanceType):
              # Guardar registro en el objeto (objeto.algo)
              node_type.addProperty(propId.getText())
          
            # Obtener el atributo de la clase (Siempre es any)
            node_type = AnyType()

          elif lexeme == "[":

            # Se está accediendo a un elemento de un array
            
            # verificar si el tipo es un array
            if not node_type.equalsType(CompilerError) and not node_type.equalsType(ArrayType):
              # error semántico
              error = SemanticError("El identificador no es un array.", line, column)
              self.addSemanticError(error)
              node_type = error
              break

            # Verificar que el tipo del índice sea numérico
            indexToken = ctx.expression(0)
            indexType = NilType() if indexToken == None else indexToken.type

            if not indexType.equalsType(CompilerError) and not indexType.equalsType(NumberType):
              # error semántico
              error = SemanticError("El índice del array debe ser de tipo numérico.", line, column)
              self.addSemanticError(error)
              node_type = error
              break

            # Si se accede correctamente, asignar el tipo de array (AnyType siempre)
            node_type = AnyType()

      # asignar el tipo del nodo
      ctx.type = node_type


    def enterPrimary(self, ctx: CompiscriptParser.PrimaryContext):
      return super().enterPrimary(ctx)
    

    def exitPrimary(self, ctx: CompiscriptParser.PrimaryContext):
      """
      Realiza las verificaciones y determina el tipo de los nodos primarios
      """
      super().exitPrimary(ctx)

      superActive = False # Indica si el nodo previo fue el lexema "super"

      for child in ctx.getChildren():
        if isinstance(child, tree.Tree.TerminalNode): # type: ignore

          token = child.getSymbol()
          type = token.type
          lexeme = child.getText()
          line = token.line
          column = token.column 

          if type == CompiscriptParser.NUMBER:
            ctx.type = NumberType()
          elif type == CompiscriptParser.STRING:
            ctx.type = StringType()
          elif lexeme == "true" or lexeme == "false":
            ctx.type = BoolType()
          elif lexeme == "nil":
            ctx.type = NilType()
          elif lexeme == "this":
            # Verificar si el scope actual es un método
            if self.symbolTable.currentScope.getParentMethod() != None:
              # Obtener la clase a la que pertenece el método y crear un tipo instancia
              classDef = self.symbolTable.currentScope.getParentClass()
              selfReferenceDef = ClassSelfReferenceType(classDef)
              ctx.type = selfReferenceDef
              
            else:
              # error semántico
              error = SemanticError("La palabra reservada 'this' solo puede ser usado dentro de un método de una clase", line, column)
              ctx.type = error
              self.addSemanticError(error)

          elif lexeme == "super":

            error = None
            # Verificar si el scope actual es una clase
            if self.symbolTable.currentScope.getParentMethod() != None:
              
              # Verificar si la clase padre existe
              classScope = self.symbolTable.currentScope.parent
              parentClassDef = classScope.reference.parent
              if parentClassDef != None:
                superActive = True
                # El tipo se determina en sig iter. según el identificador super.identificador
              else:
                # error semántico
                error = SemanticError("La clase actual no tiene una clase padre.", line, column)
            
            else:
              # error semántico
              error = SemanticError("La palabra reservada 'super' solo puede ser usado dentro de una clase.", line, column)  
          
            if error != None:
              ctx.type = error
              self.addSemanticError(error)
              break

          elif superActive and type == CompiscriptParser.IDENTIFIER:
            # Validar identificador de clase padre (super.ident)

            superActive = False
            # retornar el tipo AnyType (todas las props de clases son de tipo any)
            ctx.type = AnyType()

          
          elif type == CompiscriptParser.IDENTIFIER:
            # Verificar si el identificador existe en el scope actual
            element = self.symbolTable.currentScope.searchElement(lexeme, searchInParentScopes=True, searchInParentClasses=True)
            if element != None:
              ctx.type = element
            else:
              # error semántico
              error = SemanticError(f"El identificador '{lexeme}' no ha sido definido.", line, column)
              ctx.type = error
              self.addSemanticError(error)

          elif lexeme == "nil":
            ctx.type = NilType()

        else:
          # Es un nodo no terminal (funAnon, instanciation, expression o array)
          ctx.type = child.type

      return self.intermediateCodeGenerator.exitPrimary(ctx)

    def enterFunction(self, ctx: CompiscriptParser.FunctionContext):
      """
      Agregar función al scope actual
      """
      super().enterFunction(ctx)

      _, nodeParams = self.params.initNodeParams()

      functionName = None

      for child in ctx.children:
        if isinstance(child, tree.Tree.TerminalNodeImpl): # type: ignore
          if child.symbol.type == CompiscriptParser.IDENTIFIER:
            functionName = child.getText()
            break

          if child.symbol.getText() == "(":
            # Ya se comienza a obtener parametros
            break

      # Si no se obtuvo el nombre de la función, se agrega el scrope pero con un error
      if functionName == None:
        functionName = CompilerError("No se ha definido el nombre de la función")
        
      functionObj = FunctionType(functionName)


      # Si el scope actual es una clase
      isClassScope = self.symbolTable.currentScope.isClassScope()
      classDef = self.symbolTable.currentScope.reference
      
      if isClassScope:
        #  verificar si la función es un constructor
        if functionName == "init" and isClassScope:
          
          if classDef.constructor == None:
            # Agregar constructor a la clase
            constructorFunctionDef = classDef.addConstructor()
            nodeParams.add("reference", constructorFunctionDef) # Guardar referencia al constructor (para hijos)
          
            self.symbolTable.currentScope.addFunction(constructorFunctionDef)
            

            # Indica que el siguiente bloque es el cuerpo de un constructor
            nodeParams.add("blockType", ScopeType.CONSTRUCTOR)
            return
          
          else:
            # error semántico
            error = SemanticError("La clase ya tiene un constructor definido.", ctx.start.line, ctx.start.column)
            self.addSemanticError(error)
            ctx.type = error
        
        else:
          # Si no es un constructor, agregar como un método
          classDef.addMethod(functionName, functionObj)
      
      # No es un constructor (o hay error al agregar constructor), agregar función normal
      
      #verificar si el nombre de la función ya ha sido declarado (solo en el mismo scope)
      elementFound = self.symbolTable.currentScope.searchElement(functionName, searchInParentScopes=False, searchInParentClasses=False)
      if elementFound != None and not elementFound.equalsType(FunctionType):
          # error semántico
          error = SemanticError(f"El identificador '{functionName}' ya ha sido declarado.", ctx.start.line, ctx.start.column)
          self.addSemanticError(error)
          ctx.type = error
      else:
        # Solo agregar función si no hay otro id con el mismo nombre o si es una función (overloading o sobreescribir)
        self.symbolTable.currentScope.addFunction(functionObj)
        
      nodeParams.add("reference", functionObj) # Guardar referencia a la función (para hijos)

      # Indica que el siguiente bloque es el cuerpo de la función
      nodeParams.add("blockType", ScopeType.FUNCTION)


    def exitFunction(self, ctx: CompiscriptParser.FunctionContext):
      super().exitFunction(ctx)

      self.params.removeNodeParams()
    

    def enterParameters(self, ctx: CompiscriptParser.ParametersContext):
      """
      Agregar parámetros a la definición de la función
      """
      super().enterParameters(ctx)

      parentParams, _ = self.params.initNodeParams()

      # Obtener la definición de la función actual (guardada en parametros)
      functionDef = parentParams.get("reference")

      for child in ctx.children:
        if isinstance(child, tree.Tree.TerminalNodeImpl): # type: ignore
          if child.symbol.type == CompiscriptParser.IDENTIFIER:
            # Los parametros de la función pueden repetirse, solo se tomará el último en cuenta
            parameterName = child.getText()
            functionDef.addParam(parameterName)


    def exitParameters(self, ctx: CompiscriptParser.ParametersContext):
      super().exitParameters(ctx)

      self.params.removeNodeParams()


    def enterArguments(self, ctx: CompiscriptParser.ArgumentsContext):
      return super().enterArguments(ctx)
    

    def exitArguments(self, ctx: CompiscriptParser.ArgumentsContext):
      return super().exitArguments(ctx)
    