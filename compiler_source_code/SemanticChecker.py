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