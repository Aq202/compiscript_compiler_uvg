from enum import Enum


class TypesNames(Enum):

  NUMBER = "NUMBER"
  CHAR = "char"
  BOOL = "bool"
  CLASS = "class"
  FUNCTION = "function"
  ARRAY = "array"
  STRING = "string"
  NIL = "nil"
  OBJECT = "object"

class PrimitiveType:

  def __init__(self, name, size):
    self.name = name
    self.size = size

  def __repr__(self) -> str:
    return f"PrimitiveType(name={self.name}, size={self.size})"

primitiveTypes = {
    TypesNames.NUMBER: PrimitiveType(TypesNames.NUMBER.value, 8),
    TypesNames.CHAR: PrimitiveType(TypesNames.CHAR.value, 1),
    TypesNames.BOOL: PrimitiveType(TypesNames.BOOL.value, 1),
}

class ClassType:

  def __init__(self, name, bodyScope, parent = None):
    self.name = name
    self.parent = parent # define the parent class (inheritance)
    self.bodyScope = bodyScope # Scope of the class body

    bodyScope.reference = self # Save reference to class definition in his body scope

  def __repr__(self) -> str:
    return f"ClassType(name={self.name}, parent={self.parent})"

class FunctionType:
  
    def __init__(self, name):
      self.name = name
      self.params = []
      self.bodyScope = None
    
    def setBodyScope(self, bodyScope):
      self.bodyScope = bodyScope
      bodyScope.reference = self # Save reference to class definition in his body scope

    def addParam(self, param):
      self.params.append(param)

    def __repr__(self) -> str:
      return f"FunctionType(name={self.name}, params={self.params})"
class ArrayType:
  
    def __init__(self, name, elementType, size):
      self.name = name
      self.elementType = elementType
      self.size = size # The size is in units of the element type

    def __repr__(self) -> str:
      return f"ArrayType(name={self.name}, elementType={self.elementType}, size={self.size})"
    
class ObjectType:
  """
  Clase que empaqueta entidades como variables u objetos.
  """

  def __init__(self, name, type):
    """
    name: id del objeto
    type: tipo del objeto (debe ser la clase del objeto, ya sea primitivo o uno compuesto)
    """
    self.name = name
    self.type = type

  def __repr__(self):
    return f"ObjectType(name={self.name}, type={self.type})"

class Scope:
  
  def __init__(self, parent, level):
    self.parent = parent
    self.level = level

    self.functions = []
    self.classes = []
    self.arrays = []
    self.objects = []

    # Saves reference to class or function definition
    self.reference = None


  def addFunction(self, name):
    functionObj = FunctionType(name)
    self.functions.append(functionObj)

  def addClass(self, name, bodyScope, parent = None):
    classObj = ClassType(name, bodyScope, parent)
    self.classes.append(classObj)

  def addArray(self, name, elementType, size):
    array = ArrayType(name, elementType, size)
    self.arrays.append(array)

  def addObject(self, name, type):
    object = ObjectType(name, type)
    self.objects.append(object)

  def __repr__(self):
        return f"Scope(level={self.level}, functions={self.functions}, classes={self.classes}, arrays={self.arrays}, objects={self.objects})"

class SymbolTable:

  globalScope = Scope(None, 0)
  
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

  @staticmethod
  def addClassToCurrentScope(name, bodyScope, parent = None):
    """
    Crea una definición de clase, guardando el nombre, el bodyScope (scope propio de la clase)
    y el padre de la clase (si es que tiene)
    """
    SymbolTable.currentScope.addClass(name, bodyScope, parent = None)

  @staticmethod
  def addFunctionToCurrentScope(name):
    """
    Crea una definición de función, guardando el nombre.
    Los parámetros y el bodyScope se agregan con setters.
    """
    SymbolTable.currentScope.addFunction(name)

  def addObjectToCurrentScope(name, type):
    """
    Crea una definición de objeto, guardando el nombre y el tipo.
    """
    SymbolTable.currentScope.addObject(name, type)


  def addArrayToCurrentScope(name, elementType, size):
    """
    Crea una definición de array, guardando el nombre, el tipo de los elementos y el tamaño (en unidades de elementos).
    """
    SymbolTable.currentScope.addArray(name, elementType, size)

  @staticmethod
  def isClassScope():
    """
    Verifica si el scope actual corresponde a la definición de una clase
    """
    scope = SymbolTable.currentScope
    
    return isinstance(scope.reference, ClassType)
  
  @staticmethod
  def isFunctionScope():
    """
    Verifica si el scope actual corresponde a la definición de una función
    """
    scope = SymbolTable.currentScope

    return isinstance(scope.reference, FunctionType)
  
  @staticmethod
  def isMethodScope():
    """
    Verifica si el scope actual corresponde a la definición de un método
    """
    scope = SymbolTable.currentScope

    # Verificar que sea una función
    if not SymbolTable.isFunctionScope():
      return False
    
    # Verificar que el scope padre sea una clase
    return isinstance(scope.parent.reference, ClassType)
  

  @staticmethod
  def classExists(name):
    """
    Verifica si una clase existe en el scope actual
    """
    scope = SymbolTable.currentScope
    while scope is not None:
      for classObj in scope.classes:
        if classObj.name == name:
          return True
      scope = scope.parent

    return False
  

  @staticmethod
  def str() -> str:
    """
    Imprime todos los scopes de la tabla de símbolos.
    Comienza del scope actual y finaliza en el global.
    """
    scope = SymbolTable.currentScope
    result = "Symbol Table:"
    while scope is not None:
      result += f"\n{scope}"
      scope = scope.parent
    return result