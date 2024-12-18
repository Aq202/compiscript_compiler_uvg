from DataType import DataType, TypesNames
from primitiveTypes import AnyType, NilType
import copy
import uuid

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
    """
    Si la union tiene un solo tipo, se compara si es igual al tipo indicado.
    Si todos los tipos de la union son iguales al tipo indicado, se retorna True.
    """
    if len(self.types) != 1:
      
      return all([t.strictEqualsType(__class__) for t in self.types])
    
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
      return self

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
      self.isMethod = False
      self.id = uuid.uuid4().hex[:6]
      
    def getFunctionLevel(self):
      """
      Retorna el nivel de anidamiento de la función en la que se encuentra el objeto.
      Si es una variable global, retorna 0.
      """
      return self.bodyScope.functionLevel
    
    def getBodyOffset(self):
      return self.bodyScope.getOffset()
    
    def getRealParamsNumber(self):
      # Si es un método se agrega 1 por el this
      return len(self.params) + (1 if self.isMethod else 0)
    
    def setBodyScope(self, bodyScope):
      self.bodyScope = bodyScope
      bodyScope.reference = self # Save reference to class definition in his body scope

    def addParam(self, param):
      self.params.append(param)
    
    def setIsMethod(self, isMethod):
      self.isMethod = isMethod

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
    
    def getUniqueName(self):
      return f"{self.name}_{self.id}"

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
        
    if parent != None:
      # Copiar propiedades y métodos de la clase padre
      self.properties = copy.deepcopy(parent.properties)
      self.methods = copy.deepcopy(parent.methods)
    else:
      self.methods = dict()
      self.properties = dict() # {name: {type, index}}
    
  def addProperty(self, name, type, mergeType=False):
    """
    Se guarda el registro de que se creo una propiedad con el nombre indicado.
    MergeType: Si el tipo existe y es true, se hace un merge de los tipos.
    Si mergeType=false y la propiedad ya existe, solo se ignora.
    """
    if name not in self.properties:
      self.properties[name] = {"type": type, "index": len(self.properties)}
    
    elif mergeType and self.properties[name]["type"] != type:
      unionType = UnionType(self.properties[name]["type"], type)
      self.properties[name]["type"] = unionType
    
  def addMethod(self, name, functionObj):
    """
    Se guarda el registro de que se creo un método con el nombre indicado y parametros.
    """
    functionObj.setIsMethod(True) # Marcar que es un método
    if name not in self.methods:
      self.methods[name] = FunctionOverload(functionObj)
    else:
      self.methods[name].addOverload(functionObj)
      
  def getProperty(self, name):
    if name not in self.properties:
      return NilType()
    return self.properties.get(name)["type"]
  
  def getPropertyIndex(self, name):
    """
    Retorna la posición de la propiedad en la lista de propiedades de la clase.
    """
    return self.properties[name]["index"]
  
  def getMethod(self, name):
    if name == "init":
      return self.constructor
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
    funcDef.setIsMethod(True) # Marcar que es un método
    self.constructor = funcDef
    return funcDef
  
  def getMethodsLength(self):
    """
    Retorna la cantidad de métodos (sin contar constructor ni sobrecargas) que tiene la clase.
    """
    return len(self.methods)
    
  def __repr__(self) -> str:
    #return f"ClassType(name={self.name}, parent={self.parent}, constructor={self.constructor}, properties={self.properties}, methods={self.methods})"
    return f"ClassType(name={self.name}, parent={self.parent})"

class ClassSelfReferenceType(DataType):
  def __init__(self, classType):
    self.classType = classType

  def getType(self):
    return self
  
  def equalsType(self, __class__):
    return isinstance(self, __class__)
  
  def strictEqualsType(self, __class__):
    return isinstance(self, __class__)
  
  def getProperty(self, name):
    return self.classType.getProperty(name)
  
  def getPropertyIndex(self, name):
    """
    Retorna la posición de la propiedad en la lista de propiedades de la clase.
    """
    return self.classType.properties[name]["index"]
  
  def __repr__(self) -> str:
    return f"ClassSelfReferenceType(classType={self.classType})"
  
class InstanceType(DataType):
  def __init__(self, classType):
    self.classType = classType
    self.name = classType.name
    
    # En un inicio, realiza una copia de todas las propiedades y métodos de la clase
    # luego, guarda propiedades y métodos que se agregan posterior a instanciar la clase
    self.localProperties = copy.deepcopy(classType.properties) # {name: {type, index}}
    self.localMethods = dict() # Diccionario que guarda function overloads
    
    self.copyClassMethods()
    

  def copyClassMethods(self):
    "Copia las propiedades y métodos definidos inicialmente en la clase"
    for name, functionOverload in self.classType.methods.items():
      self.localMethods[name] = functionOverload.copy()
    
  def addProperty(self, name, type, overwriteType = False, mergeType=False):
    """
    Se guarda el registro de que se creo una propiedad con el nombre indicado.
    OverwriteType: Si el tipo existe y es true, se sobreescribe el tipo de la propiedad.
    MergeType: Si el tipo existe y es true, se hace un merge de los tipos.
    Si overwriteType=false y mergeType=false y la propiedad ya existe, solo se ignora.
    """
    if name not in self.localProperties:
      self.localProperties[name] = {"type": type, "index": len(self.localProperties)}
    
    elif overwriteType:
      self.localProperties[name]["type"] = type
    
    elif mergeType and self.localProperties[name]["type"] != type:
      unionType = UnionType(self.localProperties[name]["type"], type)
      self.localProperties[name]["type"] = unionType
    
  def addMethod(self, name, functionObj):
    """
    Se guarda el registro de que se creo un método con el nombre indicado y parametros.
    """
    if name not in self.localMethods:
      self.localMethods[name] = FunctionOverload(functionObj)
    else:
      self.localMethods[name].addOverload(functionObj)
      
  def getProperty(self, name):
    if name not in self.localProperties:
      return NilType()
    return self.localProperties.get(name)["type"]
  
  def getMethod(self, name):
    return self.localMethods.get(name)
  
  def getPropertyIndex(self, name):
    """
    Retorna la posición de la propiedad en la lista de propiedades (localProperties) del objeto.
    """
    return self.localProperties[name]["index"]
  
  def getConstructor(self):
    return self.classType.constructor
  
  def getType(self):
    return self
  
  def equalsType(self, __class__):
    return __class__ == AnyType or isinstance(self, __class__)
  
  def strictEqualsType(self, __class__):
    return isinstance(self, __class__)
  
  def __repr__(self) -> str:
    #return f"InstanceType(classType={self.classType}, localProperties={self.localProperties}, localMethods={self.localMethods})"
    return f"InstanceType(classType={self.classType.name})"
  
class ObjectType:
  """
  Clase que empaqueta entidades como variables u objetos.
  """

  def __init__(self, name, type, scope, reference = None):
    """
    name: id del objeto
    type: tipo del objeto (debe ser la clase del objeto, ya sea primitivo o uno compuesto)
    reference: si el objeto actua como una variable heredada a un scope hijo, guarda referencia al objeto
    en su scope padre. Si la referencia es None significa que es un objeto original.
    scope: referencia al scope en el que se encuentra el objeto.
    """
    self.name = name
    self.type = type
    self.scope = scope
    self.reference = reference
    self.offset = None
    self.size = None
    self.baseType = None

  def copy(self):
    obj = ObjectType(self.name, self.type, self.scope, self.reference)
    obj.assignOffset(self.offset, self.size, self.baseType)
    return obj
  
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
    return __class__ == AnyType or self.type.equalsType(__class__)
  
  def strictEqualsType(self, __class__):
    return self.type.getType().strictEqualsType(__class__)

  def setType(self, type):
    self.type = type

  def setReference(self, reference):
    self.reference = reference
    
    
  def assignOffset(self, offset, size, baseType):
    self.offset = offset
    self.size = size
    self.baseType = baseType
    
  def getFunctionLevel(self):
    """
    Retorna el nivel de anidamiento de la función en la que se encuentra el objeto.
    Si es una variable global, retorna 0.
    """
    return self.scope.functionLevel

  def __eq__(self, value: object) -> bool:
    """
    Sobreescribir el operador de igualdad para comparar si dos objetos son iguales.
    Se considera que dos objetos son iguales si tienen el mismo nombre y scope.
    """
    return isinstance(value, ObjectType) and self.name == value.name and self.scope.id == value.scope.id
  
  def __hash__(self):
    return hash((self.name, self.scope.id))
  
  def __repr__(self):
    reference = self.reference if self.reference != self else "ObjectType(SELF)"
    repr = [f"name={self.name}", f"scope={self.scope.id}"]
    if reference != None:
      repr.append(f"reference={reference}")
    if self.type != None and not self.type.strictEqualsType(AnyType):
      repr.append(f"type={self.type}")
    if self.offset != None:
      repr.append(f"offset={self.offset}")
    
    
    return f"ObjectType({', '.join(repr)})"
  
class SuperMethodWrapper(DataType):
  
  def __init__(self, method):
    """
    thisAddr: dirección de memoria del objeto que llama al método
    method: método a ejecutar.
    """
    self.method = method
  
  def getType(self):
    return self.method.getType()
  
  def equalsType(self, __class__):
    return __class__ == SuperMethodWrapper or self.method.equalsType(__class__)
  
  def strictEqualsType(self, __class__):
    print()
    return __class__ == SuperMethodWrapper or self.method.strictEqualsType(__class__)