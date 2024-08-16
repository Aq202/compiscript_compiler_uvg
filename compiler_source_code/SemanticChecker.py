from antlr4 import *
from antlr.CompiscriptListener import CompiscriptListener
from antlr.CompiscriptParser import CompiscriptParser
from SymbolTable import SymbolTable, TypesNames, primitiveTypes
from SemanticError import SemanticError

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
        classScope = SymbolTable.createScope()
        SymbolTable.addClassToCurrentScope(className, classScope, parentClassDef)

        # Cambiar al scope de la clase
        SymbolTable.setScope(classScope)

    def exitClassDecl(self, ctx: CompiscriptParser.ClassDeclContext):
      """
      Salir del scope de la clase
      """
      # Volver al scope padre
      SymbolTable.returnToParentScope()


    def enterFunction(self, ctx: CompiscriptParser.FunctionContext):
      """
      Agregar función al scope actual
      """
      for child in ctx.children:
        if isinstance(child, tree.Tree.TerminalNodeImpl):
          if child.symbol.type == CompiscriptParser.IDENTIFIER:
            functionName = child.getText()
            SymbolTable.addFunctionToCurrentScope(functionName)
            return

    def enterParameters(self, ctx: CompiscriptParser.ParametersContext):
      """
      Agregar parámetros a la definición de la función
      """
      functionDef = SymbolTable.currentScope.functions[-1]

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
      blockScope = SymbolTable.createScope()

      # Verificar si el scope corresponde a una función
      if len(SymbolTable.currentScope.functions) > 0 \
        and SymbolTable.currentScope.functions[-1].bodyScope == None:
        functionDef = SymbolTable.currentScope.functions[-1]
        
        # Agregar params al scope de la función
        for param in functionDef.params:
          blockScope.addObject(param, None)

        # Guardar el scope del bloque en la definición de la función
        functionDef.setBodyScope(blockScope)

      # Cambiar al scope del bloque
      SymbolTable.setScope(blockScope)

    def exitBlock(self, ctx: CompiscriptParser.BlockContext):
      """
      Salir del scope del bloque
      """
      SymbolTable.returnToParentScope()

    def exitPrimary(self, ctx: CompiscriptParser.PrimaryContext):
      """
      Realiza las verificaciones y determina el tipo de los nodos primarios
      """

      superActive = False # Indica si el nodo previo fue el lexema "super"

      for child in ctx.getChildren():
        if isinstance(child, tree.Tree.TerminalNode):

          token = child.getSymbol()
          type = token.type
          lexeme = child.getText()
          line = token.line
          column = token.column 

          if type == CompiscriptParser.NUMBER:
            child.type = primitiveTypes[TypesNames.NUMBER]
          elif type == CompiscriptParser.STRING:
            child.type = primitiveTypes[TypesNames.STRING]
          elif lexeme == "true" or lexeme == "false":
            child.type = primitiveTypes[TypesNames.BOOL]
          elif lexeme == "nil":
            child.type = primitiveTypes[TypesNames.NIL]
          elif lexeme == "this":
            # Verificar si el scope actual es un método
            if SymbolTable.currentScope.isMethodScope():
              classScope = SymbolTable.currentScope.parent
              classDef = classScope.reference
              child.type = classDef.getType()
              
            else:
              # error semántico
              error = SemanticError("La palabra reservada 'this' solo puede ser usado dentro de un método de una clase", line, column)
              child.type = error
              self.addSemanticError(error)

          elif lexeme == "super":

            error = None
            # Verificar si el scope actual es una clase
            if SymbolTable.currentScope.isMethodScope():
              
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
              print(SymbolTable.str())
              # error semántico
              error = SemanticError("La palabra reservada 'super' solo puede ser usado dentro de una clase.", line, column)  
          
            if error != None:
              child.type = error
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
              child.type = elemType
            else:
              # error semántico
              error = SemanticError(f"El atributo {lexeme} no existe en la clase padre.", line, column)
              child.type = error
              self.addSemanticError(error)

          
          elif type == CompiscriptParser.IDENTIFIER:
            
            # Verificar si el identificador existe en el scope actual
            elemType = SymbolTable.currentScope.getElementType(lexeme)
            if elemType != None:
              child.type = elemType
            else:
              # error semántico
              error = SemanticError(f"El identificador '{lexeme}' no ha sido definido.", line, column)
              child.type = error
              self.addSemanticError(error)

          elif lexeme == "nil":
            child.type = primitiveTypes[TypesNames.NIL]

          