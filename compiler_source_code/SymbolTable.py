from enum import Enum
import uuid
from copy import deepcopy
from primitiveTypes import AnyType
from compoundTypes import FunctionType, ClassType, ObjectType, FunctionOverload

class ScopeType(Enum):
  """
  Tipos de bloques de código
  """
  CONSTRUCTOR = "constructor"
  FUNCTION = "function"
  CLASS = "class"
  FOR_LOOP = "for_loop"
  WHILE_LOOP = "while_loop"
  CONDITIONAL = "conditional"
  GLOBAL = "global"

class Scope:
  
  def __init__(self, parent, level, type = None):
    self.parent = parent
    self.level = level
    self.type = type

    self.elements = dict()
    self.functions = dict() # Deberá ser {name: [FunctionType]}
    self.temporaries = dict() # Variables temporales creadas en el scope
  

    # Variables heredadas de un scope padre. Se agregan cuando se modifica el valor de una variable en un scope hijo.
    self.objectInheritances = dict()

    # Saves reference to class or function definition
    self.reference = None
    
    self.offset = 0 # Por defecto, el offset inicial es cero

  def addFunction(self, functionObj):
    """
    Crea una definición de función y la agrega a la lista de funciones del scope
    Si el scope actual es una clase, la función se agrega a la lista de métodos de la clase.
    @return FunctionType. Retorna el objeto de la función creada
    """
    name = functionObj.name
    
    if name not in self.functions:
      self.functions[name] = FunctionOverload(functionObj)
    else:
      self.functions[name].addOverload(functionObj)

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
    return object
    
  def addTemporary(self, name):
    temp = ObjectType(name, AnyType())
    self.temporaries[name] = temp
    return temp

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

  def searchElement(self, name, searchInParentScopes = True, searchInParentClasses = True, searchTemporaries = False):
    """
    Busca un elemento en el scope actual y padres (clase, funcion u objeto)
    @param searchInParentScopes: Bool. Buscar en los scopes padres
    @param searchInParentClasses: Bool. Buscar en las clases padres si el scope actual es una clase
    @return Objeto del elemento buscado. Si no lo encuentra retorna None.
    IMPORTANTE: si es una función, retorna una lista de funciones
    """
    scope = self
    while scope is not None:

      # Buscar en las listas de elementos
      if name in scope.elements:
        return scope.elements[name]
      if name in scope.functions:
        return scope.functions[name] # Retorna una lista de funciones
      if name in scope.objectInheritances:
        return scope.objectInheritances[name]
      if searchTemporaries and name in scope.temporaries:
        return scope.temporaries[name]
      
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
  

  def searchClass(self, name):
    """
    Busca y retorna una clase en el scope actual y en scopes padres.
    Si no la encuentra retorna None
    """
    scope = self
    while scope is not None:
      for classObj in scope.elements.values():
        if classObj.name == name:
          if isinstance(classObj, ClassType): # Si es directamente una clase
            return classObj
          elif classObj.strictEqualsType(ClassType): # Si es una variable que hace referencia a una clase
            return classObj.getType()
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
  
  def isLoopScope(self):
    """
    Verifica si el scope corresponde a un loop
    """
    return self.type == ScopeType.FOR_LOOP or self.type == ScopeType.WHILE_LOOP

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
  
  def isInsideLoop(self, searchInParentScopes = True):
    """
    Verifica si el scope actual se encuentra dentro de un loop
    """
    scope = self
    while scope is not None:
      if scope.isLoopScope():
        return True
      if not searchInParentScopes:
        break
      scope = scope.parent
    return False
  
  def isInsideConstructor(self):
    """
    Verifica si el scope actual se encuentra dentro de (o es) un constructor
    """
    scope = self
    while scope is not None:
      if scope.type == ScopeType.CONSTRUCTOR:
        return True
      scope = scope.parent
    return False

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

      if scope.type in [ScopeType.FUNCTION, ScopeType.CONDITIONAL, ScopeType.WHILE_LOOP, ScopeType.FOR_LOOP, ScopeType.CONSTRUCTOR]:
        return True
      
      scope = scope.parent
    return False
  
  def setOffset(self, offset):
    self.offset = offset

  def getInheritedObjectsList(self):
    return list(self.objectInheritances.values())
  

  def __repr__(self):
        return f"Scope(level={self.level}, type={self.type}, elements={self.elements}, functions={self.functions}, objectInheritances={self.objectInheritances}, reference={self.reference}"

class SymbolTable:

  def __init__(self):
    self.globalScope = Scope(None, 0, ScopeType.GLOBAL)
    self.currentScope = self.globalScope

  def createScope(self, type):
    return Scope(self.currentScope, self.currentScope.level + 1, type)
  
  def createScopeAndSwitch(self, type):
    newScope = self.createScope(type)
    self.setScope(newScope)
    return newScope
  
  def setScope(self, scope):
    self.currentScope = scope
    print("\n***** SCOPE MODIFICADO *****\n",self.str(),"\n")

  
  def returnToParentScope(self):
    self.setScope(self.currentScope.parent)

  def addClassToCurrentScope(self, name, bodyScope, parent = None):
    """
    Crea una definición de clase, guardando el nombre, el bodyScope (scope propio de la clase)
    y el padre de la clase (si es que tiene)
    """
    self.currentScope.addClass(name, bodyScope, parent)

  def addFunctionToCurrentScope(self, name):
    """
    Crea una definición de función, guardando el nombre.
    Los parámetros y el bodyScope se agregan con setters.
    """
    return self.currentScope.addFunction(name)

  def addObjectToCurrentScope(self, name, type):
    """
    Crea una definición de objeto, guardando el nombre y el tipo.
    """
    self.currentScope.addObject(name, type)
  

  def str(self) -> str:
    """
    Imprime todos los scopes de la tabla de símbolos.
    Comienza del scope actual y finaliza en el global.
    """
    scope = self.currentScope
    result = "Symbol Table:"
    while scope is not None:
      result += f"\n{scope}"
      scope = scope.parent
    return result