from antlr4 import *
from antlr.CompiscriptListener import CompiscriptListener
from antlr.CompiscriptParser import CompiscriptParser
from SymbolTable import SymbolTable, TypesNames, primitiveTypes, FunctionType, ClassType, PrimitiveType, ScopeType
from Errors import SemanticError, CompilerError

class SemanticChecker(CompiscriptListener):
    
    def __init__(self) -> None:
      super().__init__()

      self.errors = []

    def addSemanticError(self, error):
      self.errors.append(error)

    def enterClassDecl(self, ctx: CompiscriptParser.ClassDeclContext):
        
        """
        Guarda una nueva clase en el scope actual, creando y cambiando al scope del cuerpo de la 
        clase. Si la clase tiene una clase padre, verifica que exista en la tabla de símbolos.
        """
        super().enterClassDecl(ctx)

        # Obtener el nombre de la clase y clase heredada
        identifiers = [child for child in ctx.children 
                        if isinstance(child, tree.Tree.TerminalNodeImpl) 
                        and child.symbol.type == CompiscriptParser.IDENTIFIER]
          
        className = identifiers[0].getText()

        # Obtener clase heredada
        parentClassNode = None
        parentClassDef = None
        if len(identifiers) > 1:
          parentClassNode = identifiers[1]

          # Verificar si la clase heredada existe
          parentClassDef = SymbolTable.currentScope.searchClass(parentClassNode.getText())
          if parentClassDef == None:
            # error semántico
            parentClassToken = parentClassNode.getSymbol()
            error = SemanticError(f"La clase {parentClassNode.getText()} no existe", parentClassToken.line, parentClassToken.column)
            self.addSemanticError(error)
            

        # Crear scope para la clase y añadirlo al scope actual
        classScope = SymbolTable.createScope(ScopeType.CLASS)
        SymbolTable.addClassToCurrentScope(className, classScope, parentClassDef)

        # Cambiar al scope de la clase
        SymbolTable.setScope(classScope)

    def exitClassDecl(self, ctx: CompiscriptParser.ClassDeclContext):
      """
      Salir del scope de la clase
      """
      super().exitClassDecl(ctx)

      # Volver al scope padre
      SymbolTable.returnToParentScope()


    def enterFunction(self, ctx: CompiscriptParser.FunctionContext):
      """
      Agregar función al scope actual
      """
      super().enterFunction(ctx)

      functionName = None

      for child in ctx.children:
        if isinstance(child, tree.Tree.TerminalNodeImpl):
          if child.symbol.type == CompiscriptParser.IDENTIFIER:
            functionName = child.getText()
            break

          if child.symbol.getText() == "(":
            # Ya se comienza a obtener parametros
            break

      # Si no se obtuvo el nombre de la función, se agrega el scrope pero con un error
      if functionName == None:
        functionName = CompilerError("No se ha definido el nombre de la función")

      SymbolTable.currentScope.addFunction(functionName)
      SymbolTable.nextBlockType = ScopeType.FUNCTION # Indica que el siguiente bloque es el cuerpo de la función
      


    def enterParameters(self, ctx: CompiscriptParser.ParametersContext):
      """
      Agregar parámetros a la definición de la función
      """
      super().enterParameters(ctx)

      # Obtener la definición de la función actual (la última agregada)
      functionDef = SymbolTable.currentScope.getLastFunction()

      for child in ctx.children:
        if isinstance(child, tree.Tree.TerminalNodeImpl):
          if child.symbol.type == CompiscriptParser.IDENTIFIER:
            # Los parametros de la función pueden repetirse, solo se tomará el último en cuenta
            parameterName = child.getText()
            functionDef.addParam(parameterName)
    
    def enterBlock(self, ctx: CompiscriptParser.BlockContext):
      """
      Crear un nuevo scope para el bloque y cambiar al scope del bloque
      Si es un bloque de una función, agregar los parámetros al scope del bloque
      """
      super().enterBlock(ctx)

      # Tipo de bloque, especificado en definición previa de fun, loop o if
      blockType = SymbolTable.nextBlockType
      blockScope = SymbolTable.createScope(blockType)

      # Resetear tipo de bloque
      SymbolTable.nextBlockType = None

      # Verificar si el scope corresponde a una función
      # Si la última función no tiene definido un bodyscope, se le asigna el scope del bloque
      functionDef = SymbolTable.currentScope.getLastFunction()
      if functionDef != None and functionDef.bodyScope == None:
        
        # Agregar params al scope de la función
        for param in functionDef.params:
          blockScope.addObject(param, primitiveTypes[TypesNames.ANY])

        # Guardar el scope del bloque en la definición de la función
        functionDef.setBodyScope(blockScope)

      # Cambiar al scope del bloque
      SymbolTable.setScope(blockScope)

    def exitBlock(self, ctx: CompiscriptParser.BlockContext):
      """
      Salir del scope del bloque
      """
      super().exitBlock(ctx)

      SymbolTable.returnToParentScope()

    def exitPrimary(self, ctx: CompiscriptParser.PrimaryContext):
      """
      Realiza las verificaciones y determina el tipo de los nodos primarios
      """
      super().exitPrimary(ctx)

      superActive = False # Indica si el nodo previo fue el lexema "super"

      for child in ctx.getChildren():
        if isinstance(child, tree.Tree.TerminalNode):

          token = child.getSymbol()
          type = token.type
          lexeme = child.getText()
          line = token.line
          column = token.column 

          if type == CompiscriptParser.NUMBER:
            ctx.type = primitiveTypes[TypesNames.NUMBER]
          elif type == CompiscriptParser.STRING:
            ctx.type = primitiveTypes[TypesNames.STRING]
          elif lexeme == "true" or lexeme == "false":
            ctx.type = primitiveTypes[TypesNames.BOOL]
          elif lexeme == "nil":
            ctx.type = primitiveTypes[TypesNames.NIL]
          elif lexeme == "this":
            # Verificar si el scope actual es un método
            if SymbolTable.currentScope.getParentMethod() != None:
              classDef = SymbolTable.currentScope.getParentClass()
              ctx.type = classDef.getType()
              
            else:
              # error semántico
              error = SemanticError("La palabra reservada 'this' solo puede ser usado dentro de un método de una clase", line, column)
              ctx.type = error
              self.addSemanticError(error)

          elif lexeme == "super":

            error = None
            # Verificar si el scope actual es una clase
            if SymbolTable.currentScope.getParentMethod() != None:
              
              # Verificar si la clase padre existe
              classScope = SymbolTable.currentScope.parent
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
            # Verificar si el identificador existe en la clase padre
            classDef = SymbolTable.currentScope.parent.reference
            parentClassDef = classDef.parent
            parentClassScope = parentClassDef.bodyScope 

            elemType = parentClassScope.getElementType(lexeme, searchInParentScopes=False, searchInParentClasses=False)
            if elemType != None:
              ctx.type = elemType
            else:
              # error semántico
              error = SemanticError(f"El atributo {lexeme} no existe en la clase padre.", line, column)
              ctx.type = error
              self.addSemanticError(error)

          
          elif type == CompiscriptParser.IDENTIFIER:
            # Verificar si el identificador existe en el scope actual
            elemType = SymbolTable.currentScope.getElementType(lexeme)
            if elemType != None:
              ctx.type = elemType
            else:
              # error semántico
              error = SemanticError(f"El identificador '{lexeme}' no ha sido definido.", line, column)
              ctx.type = error
              self.addSemanticError(error)

          elif lexeme == "nil":
            ctx.type = primitiveTypes[TypesNames.NIL]

        elif isinstance(child, CompiscriptParser.FunAnonContext):
          # El nodo primario es una función anónima
          ctx.type = child.type

    def exitCall(self, ctx: CompiscriptParser.CallContext):
      super().exitCall(ctx)

      primary_name = None
      node_type = None

    
      for child in ctx.getChildren():     
        
        if isinstance(child, CompiscriptParser.PrimaryContext):
          # Obtener el tipo del nodo primario (identificador)
          primary_context = ctx.primary()

          node_type = primary_context.type
          primary_name = child.getText()

        elif isinstance(child, tree.Tree.TerminalNode):

          token = child.getSymbol()
          lexeme = child.getText()
          line = token.line
          column = token.column 

          if lexeme == "(":

            # Verificar si es una llamada a función
            if not isinstance(node_type, CompilerError) and not isinstance(node_type, FunctionType):

              # Error semántico, se está llamando a algo diferente a una función
              error = SemanticError(f"El identificador {primary_name} no es una función.", line, column)
              self.addSemanticError(error)
              ctx.type = error
              break
            elif isinstance(node_type, FunctionType):
              # Obtener el tipo de retorno de la función
              node_type = node_type.returnType

          elif lexeme == ".":
            # Se está accediendo a un atributo de un objeto

            if isinstance(node_type, CompilerError):
              break

            # Verificar si el identificador es null
            if isinstance(node_type, PrimitiveType) and node_type.name == TypesNames.NIL.value:
              # error semántico
              error = SemanticError("No se puede acceder a un atributo de un objeto nulo.", line, column)
              self.addSemanticError(error)
              node_type = error
              break
            
            if not isinstance(node_type, ClassType):
              # error semántico
              error = SemanticError(f"El identificador {primary_name} no es una clase.", line, column)
              self.addSemanticError(error)
              node_type = error
              break

          
            # Obtener el atributo de la clase, de lo contrario retornar null
            classScope = node_type.bodyScope
            attribute = ctx.IDENTIFIER(0)

            if attribute != None:
              elemType = classScope.getElementType(attribute.getText(), searchInParentScopes=True, searchInParentClasses=True)

              node_type = primitiveTypes[TypesNames.NIL] if elemType == None else elemType


      # asignar el tipo del nodo
      ctx.type = node_type
        

    def exitUnary(self, ctx: CompiscriptParser.UnaryContext):
      super().exitUnary(ctx)

      child_type = None

      for child in ctx.getChildren():
        if not isinstance(child, tree.Tree.TerminalNode):
          # Obtener el tipo del nodo hijo (unary o call)
          child_type = child.type

      # pendiente: verificar si el tipo es correcto para la operación

      # Asignar mismo tipo a este nodo
      ctx.type = child_type

    
    def exitFactor(self, ctx: CompiscriptParser.FactorContext):
      super().exitFactor(ctx)

      # Obtener el tipo de ambos nodos hijos
      child1 = ctx.unary(0)
      child1_type = child1.type if child1 else None

      # Obtener el segundo hijo 'unary' si existe
      child2 = ctx.unary(1)
      child2_type = child2.type if child2 else None

      # pendiente: verificar si el tipo es correcto para la operación


      # Asignar mismo tipo a este nodo
      ctx.type = child1_type

    def exitTerm(self, ctx: CompiscriptParser.TermContext):
      super().exitTerm(ctx)

      # Obtener el tipo de ambos nodos hijos
      child1 = ctx.factor(0)
      child1_type = child1.type if child1 else None

      child2 = ctx.factor(1)
      child2_type = child2.type if child2 else None

      # pendiente: verificar si el tipo es correcto para la operación

      # Asignar mismo tipo a este nodo
      ctx.type = child1_type

    def exitComparison(self, ctx: CompiscriptParser.ComparisonContext):
      super().exitComparison(ctx)

      # Obtener el tipo de ambos nodos hijos
      child1 = ctx.term(0)
      child1_type = child1.type if child1 else None

      child2 = ctx.term(1)
      child2_type = child2.type if child2 else None

      # pendiente: verificar si el tipo es correcto para la operación

      # Asignar mismo tipo a este nodo
      ctx.type = child1_type


    def exitEquality(self, ctx: CompiscriptParser.EqualityContext):
      super().exitEquality(ctx)

      # Obtener el tipo de ambos nodos hijos
      child1 = ctx.comparison(0)
      child1_type = child1.type if child1 else None

      child2 = ctx.comparison(1)
      child2_type = child2.type if child2 else None

      # pendiente: verificar si el tipo es correcto para la operación

      # Asignar mismo tipo a este nodo
      ctx.type = child1_type

    def exitLogic_and(self, ctx: CompiscriptParser.Logic_andContext):
      super().exitLogic_and(ctx)

      # Obtener el tipo de ambos nodos hijos
      child1 = ctx.equality(0)
      child1_type = child1.type if child1 else None

      child2 = ctx.equality(1)
      child2_type = child2.type if child2 else None

      # pendiente: verificar si el tipo es correcto para la operación

      # Asignar mismo tipo a este nodo
      ctx.type = child1_type

    def exitLogic_or(self, ctx: CompiscriptParser.Logic_orContext):
      super().exitLogic_or(ctx)

      # Obtener el tipo de ambos nodos hijos
      child1 = ctx.logic_and(0)
      child1_type = child1.type if child1 else None

      child2 = ctx.logic_and(1)
      child2_type = child2.type if child2 else None

      # pendiente: verificar si el tipo es correcto para la operación

      # Asignar mismo tipo a este nodo
      ctx.type = child1_type

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

      assignmentValueType = ctx.assignment().type
      identifier = ctx.IDENTIFIER().getText() # identificador del atributo o variable

      if ctx.call() != None:
        # Es una asignación a un atributo de clase

        receiverType = ctx.call().type # receiver = parte izq de: receiver.method_or_property()

        if isinstance(receiverType, CompilerError):
          # Si receiver es un error, solo ignorar
          ctx.type = receiverType
          return
        
        # Validar que el receiver sea un objeto de una clase
        if not isinstance(receiverType, ClassType):
          # error semántico
          line = ctx.start.line
          column = ctx.start.column
          error = SemanticError("Solo se pueden asignar atributos a objetos de una clase.", line, column)
          ctx.type = error
          self.addSemanticError(error)
          return

        # Asignar el tipo del atributo en el bodyScope de la clase
        
        bodyScope = receiverType.bodyScope
        bodyScope.addObject(identifier, assignmentValueType)
      
      else:
        # Es una asignación a variable ya declarada
        
        objectRef = SymbolTable.currentScope.getObject(identifier)

        # Verificar si el identificador existe en el scope actual
        if objectRef == None:
          # error semántico
          line = ctx.start.line
          column = ctx.start.column
          error = SemanticError(f"El identificador '{identifier}' no ha sido declarado.", line, column)
          ctx.type = error
          self.addSemanticError(error)
          return
        
        objectRef.setType(assignmentValueType)

    def exitExpression(self, ctx: CompiscriptParser.ExpressionContext):
      super().exitExpression(ctx)

      # Asignar tipo de nodo hijo
      ctx.type = ctx.getChild(0).type


    def exitExprStmt(self, ctx: CompiscriptParser.ExprStmtContext):
      super().exitExprStmt(ctx)

      # Asignar tipo de nodo hijo
      ctx.type = ctx.expression().type

    def exitVarDecl(self, ctx: CompiscriptParser.VarDeclContext):

      """
      Declaración de variables
      """
      super().exitVarDecl(ctx)

      # Validar que el nombre de la variable no sea un erro léxico
      if isinstance(ctx.IDENTIFIER(), tree.Tree.ErrorNodeImpl):
        return # Saltar validaciones semánticas de asignación de variable
      
      # Obtener nombre de variable
      identifierToken = ctx.IDENTIFIER().getSymbol()
      identifierName = identifierToken.text

      # Verificar si la variable ya ha sido declarada
      if SymbolTable.currentScope.searchElement(identifierName):
        # error semántico
        error = SemanticError(f"La variable '{identifierName}' ya ha sido declarada.", identifierToken.line, identifierToken.column)
        self.addSemanticError(error)
        ctx.type = error
        return
      
      # Obtener tipo de la variable
      varType = None
      if ctx.expression() != None:
        varType = ctx.expression().type
      else:
        varType = primitiveTypes[TypesNames.NIL]

      # Agregar variable al scope actual
      SymbolTable.currentScope.addObject(identifierName, varType)


    def exitReturnStmt(self, ctx: CompiscriptParser.ReturnStmtContext):
      super().exitReturnStmt(ctx)

      # Objeto FunctionType que corresponde al scope función que contiene la sentencia 'return'
      functionDef = SymbolTable.currentScope.getParentFunction()

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
        functionDef.setReturnType(primitiveTypes[TypesNames.NIL])
        return
      
      # Obtener tipo de la expresión y asignar al tipo de retorno
      functionDef.setReturnType(expression.type)
  

    def enterIfStmt(self, ctx: CompiscriptParser.IfStmtContext):
      super().enterIfStmt(ctx)

      # Indicar que el siguiente bloque es un bloque condicional
      SymbolTable.nextBlockType = ScopeType.CONDITIONAL

    def exitIfStmt(self, ctx: CompiscriptParser.IfStmtContext):
      super().exitIfStmt(ctx)


      # Verificar que la condición sea de tipo booleano
      condition = ctx.expression()
      if condition != None: # Si es none, es un error léxico o sintactico, ignorar
        
        if not isinstance(condition.type, PrimitiveType) or \
            (condition.type.name != TypesNames.BOOL.value and condition.type.name != TypesNames.ANY.value):
          # error semántico, la condición no es de tipo booleano o any
          line = condition.start.line
          column = condition.start.column
          error = SemanticError("La condición del if debe ser de tipo booleano.", line, column)
          self.addSemanticError(error)
          return

    def enterWhileStmt(self, ctx: CompiscriptParser.WhileStmtContext):
      super().enterWhileStmt(ctx)

      # Indicar que el siguiente bloque es un loop
      SymbolTable.nextBlockType = ScopeType.LOOP
    
    def exitWhileStmt(self, ctx: CompiscriptParser.WhileStmtContext):
      super().exitWhileStmt(ctx)

      # Verificar que la condición sea de tipo booleano
      condition = ctx.expression()
      if condition != None: # Si es none, es un error léxico o sintactico, ignorar
        
        if not isinstance(condition.type, PrimitiveType) or \
            (condition.type.name != TypesNames.BOOL.value and condition.type.name != TypesNames.ANY.value):
          # error semántico, la condición no es de tipo booleano o any
          line = condition.start.line
          column = condition.start.column
          error = SemanticError("La condición del while debe ser de tipo booleano.", line, column)
          self.addSemanticError(error)
          return

    def enterFunAnon(self, ctx: CompiscriptParser.FunAnonContext):
      super().enterFunAnon(ctx)

      # Crear y agregar una función anonima
      SymbolTable.currentScope.addAnonymousFunction()
      SymbolTable.nextBlockType = ScopeType.FUNCTION # Indica que el siguiente bloque es el cuerpo de la función

    def exitFunAnon(self, ctx: CompiscriptParser.FunAnonContext):
      super().exitFunAnon(ctx)

      # Retornar el tipo de la función (última creada) y eliminar de la tabla de símbolos
      functionDef = SymbolTable.currentScope.popLastFunction()
      ctx.type = functionDef.getType()

    def enterForStmt(self, ctx: CompiscriptParser.ForStmtContext):
      super().enterForStmt(ctx)

      # Indicar que el siguiente bloque es un loop
      SymbolTable.nextBlockType = ScopeType.LOOP


    def exitForStmt(self, ctx: CompiscriptParser.ForStmtContext):
      super().exitForStmt(ctx)

      # Verificar que segunda expresión sea de tipo booleano
      for child in ctx.children:
        if isinstance(child, CompiscriptParser.ExpressionContext):

          if isinstance(child.type, CompilerError):
            # Si el tipo de la expresión es un error, ignorar
            return

          if not isinstance(child.type, PrimitiveType) or \
              (child.type.name != TypesNames.BOOL.value and child.type.name != TypesNames.ANY.value):
            # error semántico, la condición no es de tipo booleano o any
            line = child.start.line
            column = child.start.column
            error = SemanticError("La condición del for debe ser de tipo booleano.", line, column)
            self.addSemanticError(error)
            return
        elif child.getText() == ";":
          # El punto y coma de la primera expresión no es un nodo (va incluido en la expresión como tal)
          # Cuando se encuentra un nodo terminal con ;, significa que ya se ha pasado la primera expresión
          return

    def exitProgram(self, ctx: CompiscriptParser.ProgramContext):
      super().exitProgram(ctx)
      print(SymbolTable.str())

    