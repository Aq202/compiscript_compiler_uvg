from enum import Enum

class TypesNames(Enum):

  FLOAT = "float"
  CHAR = "char"
  BOOL = "bool"
  CLASS = "class"
  FUNCTION = "function"

class PrimitiveType:

  def __init__(self, name, size):
    self.name = name
    self.size = size

class ClassType:

  def __init__(self, name, fields, bodyScope, parent = None):
    self.name = name
    self.parent = parent # define the parent class (inheritance)
    self.childScope = bodyScope # Scope of the class body

class FunctionType:
  
    def __init__(self, name,  params, bodyScope):
      self.name = name
      self.params = params
      self.bodyScope = bodyScope # Scope of the function body

class Entity:

  def __init__(self, name, type, reference = None):
    self.name = name
    self.type = type
    self.reference = reference # For functions and classes definitions

class Scope:
  
  def __init__(self, parent, level):
    self.parent = parent
    self.level = level
    self.entities = []

  def __str__(self):
        return f"Scope {self.level}"

class SymbolTable:

  globalScope = Scope(None, 0)
  primitiveTypes = {
    TypesNames.FLOAT: PrimitiveType(TypesNames.FLOAT.value, 8),
    TypesNames.CHAR: PrimitiveType(TypesNames.CHAR.value, 1),
    TypesNames.BOOL: PrimitiveType(TypesNames.BOOL.value, 1),
  }
  
  currentScope = globalScope

  @staticmethod
  def createScope():
    return Scope(SymbolTable.currentScope, SymbolTable.currentScope.level + 1)
  
  @staticmethod
  def createScopeAndSwitch():
    newScope = SymbolTable.createScope()
    SymbolTable.setScope(newScope)
    return newScope
  
  @staticmethod
  def setScope(scope):
    SymbolTable.currentScope = scope
  
  @staticmethod
  def returnToParentScope():
    SymbolTable.setScope(SymbolTable.currentScope.parent)

