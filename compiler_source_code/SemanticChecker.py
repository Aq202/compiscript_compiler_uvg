from antlr4 import *
from antlr.CompiscriptListener import CompiscriptListener
from antlr.CompiscriptParser import CompiscriptParser
from SymbolTable import SymbolTable, TypesNames, ClassType
from SemanticError import SemanticError

class SemanticChecker(CompiscriptListener):
    
    def __init__(self) -> None:
      super().__init__()

      self.errors = []

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
        if len(identifiers) > 1:
          parentClass = identifiers[1]

          # Verificar si la clase heredada existe
          if not SymbolTable.classExists(parentClass.getText()):
            # error semántico
            parentClassToken = parentClass.getSymbol()
            self.errors.append(SemanticError(f"La clase {parentClass.getText()} no existe", parentClassToken.line, parentClassToken.column))
            

        # Crear scope para la clase y añadirlo al scope actual
        classScope = SymbolTable.createScope()
        SymbolTable.addClassToCurrentScope(className, classScope, parentClass)

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
