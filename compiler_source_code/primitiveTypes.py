from DataType import DataType, TypesNames
from Errors import CompilerError

class NilType(DataType):

  def __init__(self):
    self.name = TypesNames.NIL.value

  def getType(self):
    return self
  
  def equalsType(self, __class__):
    return __class__ == NilType
  
  def strictEqualsType(self, __class__):
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
    return  __class__ != NilType and __class__ != CompilerError
  
  def strictEqualsType(self, __class__):
    return __class__ == AnyType
  
  def __repr__(self) -> str:
    return f"AnyType()"

    
class PrimitiveType(DataType):

  def __init__(self, name):
    self.name = name

  def getType(self):
    return self

  def __repr__(self) -> str:
    return f"PrimitiveType({self.name})"
  
  def equalsType(self, __class__):
    return __class__ == AnyType or isinstance(self, __class__)
  
  def strictEqualsType(self, __class__):
    return isinstance(self, __class__)

class NumberType(PrimitiveType):
  def __init__(self):
    super().__init__(TypesNames.NUMBER.value)

  def __eq__(self, other):
    # Sobreescribir __eq__ para que todos los objetos de NumberType sean iguales
    return isinstance(other, NumberType)
  
class StringType(PrimitiveType):
  def __init__(self):
    super().__init__(TypesNames.STRING.value)

  def __eq__(self, other):
    # Sobreescribir __eq__ para que todos los objetos de StringType sean iguales
    return isinstance(other, StringType) 

class BoolType(PrimitiveType):
  def __init__(self):
    super().__init__(TypesNames.BOOL.value)

  def __eq__(self, other):
    # Sobreescribir __eq__ para que todos los objetos de BoolType sean iguales
    return isinstance(other, BoolType)
