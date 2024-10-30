from enum import Enum

class RegisterTypes(Enum):

  saved = "s"
  temporary = "t"
  float = "f"
  valueReturn = "v"
  arguments = "a"
  globalPointer = "gp"
  stackPointer = "sp"
  framePointer = "fp"
  returnAddress = "ra"
  
class Register:
  
  def __init__(self, type, number):
    self.type = type
    self.number = number
    
  def __eq__(self, obj):
    return obj.type == self.type and obj.number == self.number
  
  def __hash__(self):
    return hash((self.type, self.number))