from enum import Enum
from abc import ABC, abstractmethod
class TypesNames(Enum):

  NUMBER = "NUMBER"
  BOOL = "bool"
  CLASS = "class"
  FUNCTION = "function"
  ARRAY = "array"
  STRING = "string"
  NIL = "nil"
  OBJECT = "object"
  ANY = "any"

class DataType(ABC):
    
    @abstractmethod
    def getType(self):
        pass

class PrimitiveType(DataType):

  def __init__(self, name, size):
    self.name = name
    self.size = size

  def getType(self):
    return self

  def __repr__(self) -> str:
    return f"PrimitiveType(name={self.name}, size={self.size})"

primitiveTypes = {
    TypesNames.NUMBER: PrimitiveType(TypesNames.NUMBER.value, 1),
    TypesNames.STRING: PrimitiveType(TypesNames.STRING.value, 1),
    TypesNames.BOOL: PrimitiveType(TypesNames.BOOL.value, 1),
    TypesNames.NIL: PrimitiveType(TypesNames.NIL.value, 0),
    TypesNames.ANY: PrimitiveType(TypesNames.ANY.value, 0),
}


class ClassType(DataType):

  def __init__(self, name, bodyScope, parent = None):
    self.name = name
    self.parent = parent # define the parent class (inheritance)
    self.bodyScope = bodyScope # Scope of the class body

    bodyScope.reference = self # Save reference to class definition in his body scope

  def getType(self):
    return self
    
  def __repr__(self) -> str:
    return f"ClassType(name={self.name}, parent={self.parent})"

class FunctionType:
  
    def __init__(self, name):
      self.name = name
      self.params = []
      self.bodyScope = None
      self.returnType = PrimitiveType(TypesNames.NIL.value, 0)
    
    def setBodyScope(self, bodyScope):
      self.bodyScope = bodyScope
      bodyScope.reference = self # Save reference to class definition in his body scope

    def addParam(self, param):
      self.params.append(param)

    def getType(self):
      return self
    
    def setReturnType(self, returnType):
      self.returnType = returnType

    def getParamsInReverseOrder(self):
      return self.params[::-1]

    def __repr__(self) -> str:
      return f"FunctionType(name={self.name}, params={self.params}, returnType={self.returnType})"
class ArrayType:
  
    def __init__(self, name, elementType, size):
      self.name = name
      self.elementType = elementType
      self.size = size # The size is in units of the element type

    def getType(self):
      self

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

  def getType(self):
    return self.type

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
    """
    Crea una definición de función y la agrega a la lista de funciones del scope
    @return FunctionType. Retorna el objeto de la función creada
    """
    functionObj = FunctionType(name)
    self.functions.insert(0, functionObj)
    return functionObj

  def addClass(self, name, bodyScope, parent = None):
    classObj = ClassType(name, bodyScope, parent)
    self.classes.insert(0, classObj)

  def addArray(self, name, elementType, size):
    array = ArrayType(name, elementType, size)
    self.arrays.insert(0, array)

  def addObject(self, name, type):
    object = ObjectType(name, type)
    self.objects.insert(0, object)

  def searchElement(self, name, searchInParentScopes = True, searchInParentClasses = True):
    """
    Busca un elemento en el scope actual y padres (clase, funcion, array u objeto)
    @param searchInParentScopes: Bool. Buscar en los scopes padres
    @param searchInParentClasses: Bool. Buscar en las clases padres si el scope actual es una clase
    @return Objeto del elemento buscado. Si no lo encuentra retorna None.
    """
    scope = self
    while scope is not None:

      # Buscar en las listas de elementos
      for element in scope.functions + scope.classes + scope.arrays + scope.objects:
        if element.name == name:
          return element
      
      # Buscar en la clase padre si es una clase
      if searchInParentClasses and scope.isClassScope():
        classDef = scope.reference
        parentClass = classDef.parent
        if parentClass is not None:
          # Buscar en el scope de la clase padre
          parentClassScope = parentClass.bodyScope
          element = parentClassScope.searchElement(name, searchInParentScopes=False, searchInParentClasses=False)
          if element is not None:
            return element
          
      # Si no se debe buscar en los scopes padres, salir del ciclo
      if not searchInParentScopes:
        break
      scope = scope.parent

    return None
  
  def getElementType(self, name, searchInParentScopes = True, searchInParentClasses = True):
    """
    Retorna el tipo de un elemento en el scope
    Si no lo encuentra retorna None
    """
    element = self.searchElement(name, searchInParentScopes, searchInParentClasses)
    if element is None:
      return None
    return element.getType()

  def searchClass(self, name):
    """
    Busca y retorna una clase en el scope actual y en scopes padres.
    Si no la encuentra retorna None
    """
    scope = SymbolTable.currentScope
    while scope is not None:
      for classObj in scope.classes:
        if classObj.name == name:
          return classObj
      scope = scope.parent

    return None
  
  def isClassScope(self):
    """
    Verifica si el scope corresponde a la definición de una clase
    """
    return isinstance(self.reference, ClassType)
  
  def isFunctionScope(self):
    """
    Verifica si el scope corresponde a la definición de una función
    """
    return isinstance(self.reference, FunctionType)
  

  def isMethodScope(self):
    """
    Verifica si el scope actual corresponde a la definición de un método (Función dentro de una clase)
    """
    # Verificar que sea una función
    if not self.isFunctionScope():
      return False
    
    # Verificar que no sea el scope global
    if self.parent is None:
      return False
    
    # Verificar que el scope padre sea una clase
    return self.parent.isClassScope()

  def getParentFunction(self):
    """
    Obtiene la definición de la función padre (o del él mismo) del scope actual.
    Si no es un scope de función ni posee un scope padre que lo sea, retorna None.
    @return FunctionType
    """
    if self.isFunctionScope():
      return self.reference
    
    # Verificar si es un scope hijo de una función
    while (scope := self.parent) is not None:
      if scope.isFunctionScope():
        return scope.reference
      
    return None
  
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
    SymbolTable.currentScope.addClass(name, bodyScope, parent)

  @staticmethod
  def addFunctionToCurrentScope(name):
    """
    Crea una definición de función, guardando el nombre.
    Los parámetros y el bodyScope se agregan con setters.
    """
    return SymbolTable.currentScope.addFunction(name)

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