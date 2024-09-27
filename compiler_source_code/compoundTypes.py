from DataType import DataType, TypesNames
from primitiveTypes import AnyType, NilType

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
    return __class__ == AnyType or any([t.equalsType(__class__) for t in self.types])
  
  def strictEqualsType(self, __class__):
    if len(self.types) != 1:
      return False
    
    return self.types[0].strictEqualsType(__class__)
    
  
  def includesType(self, type):
    print([isinstance(typeObj, type) for typeObj in self.types])
    return any(isinstance(typeObj, type) for typeObj in self.types)

  def __repr__(self) -> str:
    return f"UnionType({', '.join([str(t) for t in self.types])})"
  

class ArrayType(DataType):
  
    def __init__(self):
      self.name = TypesNames.ARRAY.value

    def getType(self):
      self

    def equalsType(self, __class__):
      return __class__ == AnyType or isinstance(self, __class__)
    
    def strictEqualsType(self, __class__):
      return isinstance(self, __class__)
    
    def __eq__(self, other):
      # Sobreescribir __eq__ para que todos los objetos de ArrayType sean iguales
      return isinstance(other, ArrayType)

    def __repr__(self) -> str:
      return f"ArrayType()"

class FunctionType:
  
    def __init__(self, name):
      self.name = name
      self.params = []
      self.bodyScope = None
      self.returnType = NilType()
      self.returnTypeHasChanged = False
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
    
    def strictEqualsType(self, __class__):
      return isinstance(self, __class__)
    
    def setReturnType(self, returnType, preventOverwrite = False):
      if self.blockReturnTypeChange == True:
        return
      
      self.returnTypeHasChanged = True
      self.returnType = returnType
      self.blockReturnTypeChange = preventOverwrite

    def getParamsInReverseOrder(self):
      return self.params[::-1]

    def __repr__(self) -> str:
      returnType = self.returnType if self.returnType != self else "FunctionType(SELF)"
      return f"FunctionType(name={self.name}, params={self.params}, returnType={returnType})"

class FunctionOverload(DataType):
  def __init__(self, *functionDef):
    self.overloads = list(functionDef)
  
  def addOverload(self, functionDef):
    """
    Agrega una definición de función a la lista de sobrecargas.
    La sobrecarga más reciente se agrega al inicio de la lista, sobreescribiendo las anteriores con
    mismo # de parámetros.
    """
    self.overloads.insert(0, functionDef)
  
  def getOverloads(self):
    return self.overloads
  
  def getFunctionByParams(self, numParams):
    """
    Retorna la definición de la función que tiene el número de parámetros indicado.
    Si no existe una definición con ese número de parámetros, retorna la primera definición.
    """
    for overload in self.overloads:
      if len(overload.params) == numParams:
        return overload
    return self.overloads[0]
  
  def getType(self):
    return self
  
  def equalsType(self, __class__):
    return __class__ == AnyType or isinstance(self.overloads[0], __class__) or isinstance(self, __class__)
  
  def strictEqualsType(self, __class__):
      return isinstance(self, __class__)
  
  def __repr__(self) -> str:
    return f"FunctionOverload(overloads={self.overloads})"
  
  def copy(self):
    """
    Copia superficial.
    Retorna una nueva instancia de FunctionOverload, manteniendo las referencias de objetos internos.
    """
    return FunctionOverload(*self.overloads)

class ClassType(DataType):

  def __init__(self, name, bodyScope, parent = None):
    self.name = name
    self.parent = parent # define the parent class (inheritance)
    self.bodyScope = bodyScope # Scope of the class body
    self.constructor = None # Se pueden guardar varios constructores, con distintos # de params

    bodyScope.reference = self # Save reference to class definition in his body scope
    
    self.properties = []
    self.methods = dict()
    
  def addProperty(self, name):
    """
    Se guarda el registro de que se creo una propiedad con el nombre indicado.
    """
    if name not in self.properties:
      self.properties.append(name)
    
  def addMethod(self, name, functionObj):
    """
    Se guarda el registro de que se creo un método con el nombre indicado y parametros.
    """
    if name not in self.methods:
      self.methods[name] = FunctionOverload(functionObj)
    else:
      self.methods[name].addOverload(functionObj)
      
  def searchProperty(self, name):
    return self.properties.get(name)
  
  def searchMethod(self, name):
    return self.methods.get(name)

  def equalsType(self, __class__):
    # Para clases, solo se compara si son exactamente iguales
    return __class__ == ClassType
  
  def strictEqualsType(self, __class__):
    return __class__ == ClassType
  
  def getType(self):
    return self
  
  def getParentScope(self):
    if self.parent is None:
      return None
    return self.parent.bodyScope
  
  def addConstructor(self):
    funcDef = FunctionType("init")
    self.constructor = funcDef
    return funcDef
    
  def __repr__(self) -> str:
    return f"ClassType(name={self.name}, parent={self.parent}, constructor={self.constructor}, properties={self.properties}, methods={self.methods})"

class ClassSelfReferenceType(DataType):
  def __init__(self, classType):
    self.classType = classType

  def getType(self):
    return self
  
  def equalsType(self, __class__):
    return isinstance(self, __class__)
  
  def strictEqualsType(self, __class__):
    return isinstance(self, __class__)
  
  def __repr__(self) -> str:
    return f"ClassSelfReferenceType(classType={self.classType})"
  
class InstanceType(DataType):
  def __init__(self, classType):
    self.classType = classType
    self.name = classType.name
    
    # En un inicio, realiza una copia de todas las propiedades y métodos de la clase
    # luego, guarda propiedades y métodos que se agregan posterior a instanciar la clase
    # No es para guardar tipos, solo para verificar que en algún momento se agregó la prop o método
    self.localProperties = classType.properties.copy()
    self.localMethods = dict() # Diccionario que guarda function overloads
    
    self.copyClassMethods()
    

  def copyClassMethods(self):
    "Copia las propiedades y métodos definidos inicialmente en la clase"
    for name, functionOverload in self.classType.methods.items():
      self.localMethods[name] = functionOverload.copy()
    
  def addProperty(self, name):
    """
    Se guarda el registro de que se creo una propiedad con el nombre indicado.
    """
    if name not in self.localProperties:
      self.localProperties.append(name)
    
  def addMethod(self, name, functionObj):
    """
    Se guarda el registro de que se creo un método con el nombre indicado y parametros.
    """
    if name not in self.localMethods:
      self.localMethods[name] = FunctionOverload(functionObj)
    else:
      self.localMethods[name].addOverload(functionObj)
      
  def searchProperty(self, name):
    return self.localProperties.get(name)
  
  def searchMethod(self, name):
    return self.localMethods.get(name)
  
  def getType(self):
    return self
  
  def equalsType(self, __class__):
    return __class__ == AnyType or isinstance(self, __class__)
  
  def strictEqualsType(self, __class__):
    return isinstance(self, __class__)
  
  def __repr__(self) -> str:
    return f"InstanceType(classType={self.classType}, localProperties={self.localProperties}, localMethods={self.localMethods})"
  
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
    self.value = None

  def getType(self):
    """
    Devuelve el tipo guardado en la variable.
    Si hay otra variable, itera hasta obtener el tipo final.
    """
    type = self.type
    while isinstance(type, ObjectType):
      type = type.getType()
    
    return type

  def equalsType(self, __class__):
    return __class__ == AnyType or isinstance(self.type, __class__)
  
  def strictEqualsType(self, __class__):
    return isinstance(self.type, __class__)

  def setType(self, type):
    self.type = type

  def setReference(self, reference):
    self.reference = reference
    
  def setValue(self, value):
    """
    El valor de un objeto deberá ser un valor primitivo o una "variable" (ObjectType)
    No debe contener clases ni funciones.
    """
    
    # Validar que es un tipo primitivo o un ObjectType
    validTypes = (int, float, bool, str, ObjectType)
    if not isinstance(value, validTypes):
      raise ValueError(f"El valor de un objeto debe ser un tipo primitivo o un ObjectType. Se recibió {type(value)}")
    
    self.value = value

  def __repr__(self):
    reference = self.reference if self.reference != self else "ObjectType(SELF)"
    return f"ObjectType(name={self.name}, type={self.type}, reference={reference}, value={self.value})"
