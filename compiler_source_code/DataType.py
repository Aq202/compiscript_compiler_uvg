from abc import ABC, abstractmethod
from enum import Enum

class DataType(ABC):
  
  @abstractmethod
  def getType(self):
    pass
  
  @abstractmethod
  def equalsType(self, __class__):
    pass
  
  @abstractmethod
  def strictEqualsType(self, __class__):
    pass
  
class TypesNames(Enum):

  INT = "int"
  FLOAT = "float"
  NUMBER = "number"
  BOOL = "bool"
  CLASS = "class"
  FUNCTION = "function"
  ARRAY = "array"
  STRING = "string"
  NIL = "nil"
  OBJECT = "object"
  ANY = "any"