from enum import Enum
from abc import ABC, abstractmethod
import uuid
from copy import deepcopy
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

class ScopeType(Enum):
  """
  Tipos de bloques de código
  """
  FUNCTION = "function"
  CLASS = "class"
  LOOP = "loop"
  CONDITIONAL = "conditional"
  GLOBAL = "global"

class DataType(ABC):
    
    @abstractmethod
    def getType(self):
        pass
    
    @abstractmethod
    def equalsType(self, __class__):
        pass
    
class NilType(DataType):

  def __init__(self):
    self.name = TypesNames.NIL.value
    self.size = 0

  def getType(self):
    return self
  
  def equalsType(self, __class__):
    return __class__ == NilType

  def __eq__(self, other):
    # Sobreescribir __eq__ para que todos los objetos de NilType sean iguales
    return isinstance(other, NilType)
  
  def __repr__(self) -> str:
    return f"NilType()"



class AnyType(DataType):
    
  def __eq__(self, other):
    # Sobreescribir __eq__ para que todos los objetos de AnyType sean iguales
    return isinstance(other, AnyType)
  
  def getType(self):
    return self
  
  def equalsType(self, __class__):
    return  __class__ != NilType
  
  def __repr__(self) -> str:
    return f"AnyType()"

class UnionType(DataType):
  def __init__(self, *types):
    self.types = []
    for t in types:
      if isinstance(t, UnionType):
        # Si es una union, agregar todos los tipos de la union
        for t2 in t.types:
          self.addType(t2)
      else:
        self.addType(t)

  def addType(self, type):
    if type not in self.types:
      self.types.append(type)

  def getType(self):
    return self
  
  def equalsType(self, __class__):
    return __class__ == AnyType or any([t.isCompatible(__class__) for t in self.types])
  
  def includesType(self, type):
    print([isinstance(typeObj, type) for typeObj in self.types])
    return any(isinstance(typeObj, type) for typeObj in self.types)

  def __repr__(self) -> str:
    return f"UnionType({', '.join([str(t) for t in self.types])})"
    
class PrimitiveType(DataType):

  def __init__(self, name, size):
    self.name = name
    self.size = size

  def getType(self):
    return self

  def __repr__(self) -> str:
    return f"PrimitiveType(name={self.name}, size={self.size})"
  
  def equalsType(self, __class__):
    return __class__ == AnyType or isinstance(self, __class__)
  

class NumberType(PrimitiveType):
  def __init__(self):
    super().__init__(TypesNames.NUMBER.value, 1)

  def __eq__(self, other):
    # Sobreescribir __eq__ para que todos los objetos de NumberType sean iguales
    return isinstance(other, NumberType)
  
class StringType(PrimitiveType):
  def __init__(self):
    super().__init__(TypesNames.STRING.value, 1)

  def __eq__(self, other):
    # Sobreescribir __eq__ para que todos los objetos de StringType sean iguales
    return isinstance(other, StringType) 

class BoolType(PrimitiveType):
  def __init__(self):
    super().__init__(TypesNames.BOOL.value, 1)

  def __eq__(self, other):
    # Sobreescribir __eq__ para que todos los objetos de BoolType sean iguales
    return isinstance(other, BoolType)


class ClassType(DataType):

  def __init__(self, name, bodyScope, parent = None):
    self.name = name
    self.parent = parent # define the parent class (inheritance)
    self.bodyScope = bodyScope # Scope of the class body

    bodyScope.reference = self # Save reference to class definition in his body scope

  def equalsType(self, __class__):
    # Para clases, solo se compara si son exactamente iguales
    return __class__ == ClassType
  
  def getType(self):
    return self
  
  def getParentScope(self):
    if self.parent is None:
      return None
    return self.parent.bodyScope
    
  def __repr__(self) -> str:
    return f"ClassType(name={self.name}, parent={self.parent})"

class FunctionType:
  
    def __init__(self, name):
      self.name = name
      self.params = []
      self.bodyScope = None
      self.returnType = None
      self.blockReturnTypeChange = False
    
    def setBodyScope(self, bodyScope):
      self.bodyScope = bodyScope
      bodyScope.reference = self # Save reference to class definition in his body scope

    def addParam(self, param):
      self.params.append(param)

    def getType(self):
      return self
    
    def equalsType(self, __class__):
      return __class__ == AnyType or isinstance(self, __class__)
    
    def setReturnType(self, returnType, preventOverwrite = False):
      if self.blockReturnTypeChange == True:
        return
      
      self.returnType = returnType
      self.blockReturnTypeChange = preventOverwrite

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

    def equalsType(self, __class__):
      return __class__ == AnyType or isinstance(self, __class__)

    def __repr__(self) -> str:
      return f"ArrayType(name={self.name}, elementType={self.elementType}, size={self.size})"
    
class ObjectType:
  """
  Clase que empaqueta entidades como variables u objetos.
  """

  def __init__(self, name, type, reference = None):
    """
    name: id del objeto
    type: tipo del objeto (debe ser la clase del objeto, ya sea primitivo o uno compuesto)
    reference: si el objeto actua como una variable heredada a un scope hijo, guarda referencia al objeto
    en su scope padre. Si la referencia es None significa que es un objeto original.
    """
    self.name = name
    self.type = type
    self.reference = reference

  def getType(self):
    return self.type

  def equalsType(self, __class__):
    return __class__ == AnyType or isinstance(self.type, __class__)

  def setType(self, type):
    self.type = type

  def setReference(self, reference):
    self.reference = reference

  def __repr__(self):
    return f"ObjectType(name={self.name}, type={self.type}, reference={self.reference})"

class Scope:
  
  def __init__(self, parent, level, type = None):
    self.parent = parent
    self.level = level
    self.type = type

    self.elements = dict()
    self.properties = dict()

  

    # Variables heredadas de un scope padre. Se agregan cuando se modifica el valor de una variable en un scope hijo.
    self.objectInheritances = dict()
    self.propertyInheritances = dict()

    # Saves reference to class or function definition
    self.reference = None


  def addFunction(self, name):
    """
    Crea una definición de función y la agrega a la lista de funciones del scope
    Si el scope actual es una clase, la función se agrega a la lista de métodos de la clase.
    @return FunctionType. Retorna el objeto de la función creada
    """
    functionObj = FunctionType(name)

    if self.type == ScopeType.CLASS:
      self.properties[name] = functionObj
    else:
      self.elements[name] = functionObj

      
    return functionObj
  
  def addAnonymousFunction(self):
    """
    Crea una definición de función anónima y la agrega a la lista de funciones del scope
    @return FunctionType. Retorna el objeto de la función creada
    """
    functionObj = FunctionType(f"anonymous_{uuid.uuid4()}")
    self.elements[functionObj.name] = functionObj
    return functionObj
  
  def popLastFunction(self):
    """
    Elimina la última función definida en el scope actual y lo retorna.
    """
    if len(self.elements) == 0:
      return None
    
    for key in reversed(self.elements.keys()):
      if isinstance(self.elements[key], FunctionType):
        return self.elements.pop(key)


  def addClass(self, name, bodyScope, parent = None):
    classObj = ClassType(name, bodyScope, parent)
    self.elements[name] = classObj

  def addObject(self, name, type):
    object = ObjectType(name, type)
    self.elements[name] = object

  def addProperty(self, name, type):
    object = ObjectType(name, type)
    self.properties[name] = object

  def modifyInheritedObjectType(self, originalObject, newType):
    """
    Crea una copia de de un objeto heredado en un scope hijo para modificar su tipo.
    """
    if originalObject.name in self.objectInheritances:
      self.objectInheritances[originalObject.name].setType(newType)
    else:
      copy = deepcopy(originalObject)
      copy.setType(newType)
      copy.setReference(originalObject)

      self.objectInheritances[originalObject.name] = copy

  def modifyInheritedPropertyType(self, originalParam, newType):
    """
    Crea una copia de de un objeto heredado en un scope hijo para modificar su tipo.
    """
    if originalParam.name in self.propertyInheritances:
      self.propertyInheritances[originalParam.name].setType(newType)
    else:
      copy = deepcopy(originalParam)
      copy.setType(newType)
      copy.setReference(originalParam)

      self.propertyInheritances[originalParam.name] = copy

  def searchElement(self, name, searchInParentScopes = True, searchInParentClasses = True):
    """
    Busca un elemento en el scope actual y padres (clase, funcion u objeto)
    @param searchInParentScopes: Bool. Buscar en los scopes padres
    @param searchInParentClasses: Bool. Buscar en las clases padres si el scope actual es una clase
    @return Objeto del elemento buscado. Si no lo encuentra retorna None.
    """
    scope = self
    while scope is not None:

      # Buscar en las listas de elementos
      if name in scope.elements:
        return scope.elements[name]
      if name in scope.objectInheritances:
        return scope.objectInheritances[name]
      
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
  
  def getObject(self, name, searchInParentScopes = True):
    """
    Retorna el objeto de una variable en el scope actual o en scopes padres.
    Si no lo encuentra retorna None
    """
    scope = self
    while scope is not None:

      # Buscar en las listas de variables (objetos)
      if name in scope.elements and isinstance(scope.elements[name], ObjectType):
        return scope.elements[name]
      
      if name in scope.objectInheritances:
        return scope.objectInheritances[name]

      if not searchInParentScopes:
        break

      scope = scope.parent

    return None
  
  def getProperty(self, name, searchInParentScopes = True):
    """
    Retorna el objeto de un parametro en el scope actual o en scopes padres.
    Al finalizar la búsqueda en el primer scope de tipo CLASS, detiene la búsqueda.
    Si no lo encuentra retorna None
    """
    scope = self
    while scope is not None:

      # Buscar en las listas de parametros (solo para scope de clase)
      if name in scope.properties:
        return scope.properties[name]
      
      if name in scope.propertyInheritances:
        return scope.propertyInheritances[name]

      if not searchInParentScopes or scope.type == ScopeType.CLASS:
        break

      scope = scope.parent

    return None

  def searchClass(self, name):
    """
    Busca y retorna una clase en el scope actual y en scopes padres.
    Si no la encuentra retorna None
    """
    scope = SymbolTable.currentScope
    while scope is not None:
      for classObj in scope.elements.values():
        if isinstance(classObj, ClassType) and classObj.name == name:
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

  def getParentFunction(self, searchInParentScopes = True):
    """
    Obtiene la definición de la función padre (o del él mismo) del scope actual.
    Si no es un scope de función ni posee un scope padre que lo sea, retorna None.
    Si searchInParentScopes no es True, solo se retorna la definición de la función del scope actual (si existe).
    @param searchInParentScopes: Bool. Buscar en los scopes padres
    @return FunctionType
    """
    if self.isFunctionScope():
      return self.reference
    
    if not searchInParentScopes:
      return None

    # Verificar si es un scope hijo de una función
    scope = self
    while (scope := scope.parent) is not None:
      if scope.isFunctionScope():
        return scope.reference
      
    return None
  
  def getParentMethod(self, searchInParentScopes = True):
    """
    Obtiene la definición del método padre (o del él mismo) del scope actual.
    Si no es un scope de método ni posee un scope padre que lo sea, retorna None.
    Si searchInParentScopes no es True, solo se retorna la definición de la función del scope actual (si existe).
    @param searchInParentScopes: Bool. Buscar en los scopes padres
    @return FunctionType
    """
    if self.isMethodScope():
      return self.reference

    if not searchInParentScopes:
      return None
    
    # Verificar si es un scope hijo de un método
    scope = self
    while (scope := scope.parent) is not None:
      if scope.isMethodScope():
        return scope.reference
      
    return None
  
  def getParentClass(self, searchInParentScopes = True):
    """
    Obtiene la definición de la clase padre (o del él mismo) del scope actual.
    Si no es un scope de clase ni posee un scope padre que lo sea, retorna None.
    Si searchInParentScopes no es True, solo se retorna la definición de la función del scope actual (si existe).
    @param searchInParentScopes: Bool. Buscar en los scopes padres
    @return ClassType
    """
    if self.isClassScope():
      return self.reference
    
    if not searchInParentScopes:
      return None

    # Verificar si es un scope hijo de una clase
    scope = self
    while (scope := scope.parent) is not None:
      if scope.isClassScope():
        return scope.reference
      
    return None
  
  def getLastFunction(self):
    """
    Retorna la última función definida (si existe) en el scope actual.
    Si el scope es de tipo CLASS devuelve las funciones definidas como propiedades.
    Si no hay funciones, retorna None.

    IMPORTANTE: Si una función es redefinida, el orden se mantiene siempre, esta no se coloca al final.
    """
    scopeElements = self.elements
    if self.type == ScopeType.CLASS:
      scopeElements = self.properties

    if len(scopeElements) == 0:
      return None
    
    for elem in reversed(scopeElements.values()):
      if isinstance(elem, FunctionType):
        return elem

  def isExecutionAmbiguous(self, elementStop):
    """
    Verifica si el punto de ejecución actual podría o no ejecutarse. Un punto de ejecución es 
    ambiguo si se encuentra dentro de una función, condicional o loop.
    @param elementStop. Se detiene la búsqueda si se encuentra la definición del elemento en un scope
    o si el mismo scope hace referencia al elemento (es cuerpo de una clase o función)
    Dicho scope ya no es tomado en cuenta para la verificación y si para ese momento no se ha encontrado
    un scope de tipo FUNCTION, CONDITIONAL o LOOP, se retorna False.
    
    ElementStop no puede ser un método o propiedad de una clase. Para estos casos, se debe utilizar 
    la definición de la clase.
    """
    scope = self
    while scope is not None:

      # verificar si el scope actual hace referencia al elemento (es su cuerpo)
      if scope.reference == elementStop:
        return False

      # Verificar si scope actual contiene a elementStop
      if elementStop is not None:
        if elementStop.name in scope.elements and scope.elements[elementStop.name] == elementStop:
          return False
        if elementStop.name in scope.objectInheritances and scope.objectInheritances[elementStop.name] == elementStop:
          return False

      if scope.type in [ScopeType.FUNCTION, ScopeType.CONDITIONAL, ScopeType.LOOP]:
        return True
      
      scope = scope.parent
    return False

  def getInheritedObjectsList(self):
    return list(self.objectInheritances.values())
  
  def getInheritedPropertiesList(self):
    return list(self.propertyInheritances.values())

  def __repr__(self):
        return f"Scope(level={self.level}, type={self.type}, elements={self.elements}, properties={self.properties}, objectInheritances={self.objectInheritances}, parameterInheritances={self.propertyInheritances}"

class SymbolTable:

  globalScope = Scope(None, 0, ScopeType.GLOBAL)
  
  currentScope = globalScope
  nextBlockType = None

  @staticmethod
  def createScope(type):
    return Scope(SymbolTable.currentScope, SymbolTable.currentScope.level + 1, type)
  
  @staticmethod
  def createScopeAndSwitch(type):
    newScope = SymbolTable.createScope()
    SymbolTable.setScope(newScope)
    return newScope
  
  @staticmethod
  def setScope(scope):
    SymbolTable.currentScope = scope
    print("\n***** SCOPE MODIFICADO *****\n",SymbolTable.str(),"\n")

  
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