from enum import Enum

class RegisterTypes(Enum):

  zero = "zero"
  saved = "s"
  temporary = "t"
  valueReturn = "v"
  arguments = "a"
  globalPointer = "gp"
  stackPointer = "sp"
  framePointer = "fp"
  returnAddress = "ra"
  floatTemporary = "f"
  floatSaved = "f"
  
class Register:
  
  def __init__(self, type, number):
    self.type = type
    self.number = number
    
  def __eq__(self, obj):
    if self.number != None:
      return obj.type == self.type and obj.number == self.number
    return obj.type == self.type
  
  def __hash__(self):
    if self.number == None:
      return hash(self.type)
    return hash((self.type, self.number))
  
  def __str__(self) -> str:
    if self.number == None:
      return f"{self.type.value}"
    return f"${self.type.value}{self.number}"
  
  def __repr__(self) -> str:
    if self.number == None:
      return f"{self.type.value}"
    return f"${self.type.value}{self.number}"
  
zero = Register(RegisterTypes.zero, None)
valueReturn = tuple(Register(RegisterTypes.valueReturn, i) for i in range(2))
arguments = tuple(Register(RegisterTypes.arguments, i) for i in range(4))
temporary = tuple(Register(RegisterTypes.temporary, i) for i in range(10))
saved = tuple(Register(RegisterTypes.saved, i) for i in range(8))
compilerTemporary = tuple(Register(RegisterTypes.temporary, i) for i in range(8,10))
globalPointer = Register(RegisterTypes.globalPointer, None)
stackPointer = Register(RegisterTypes.stackPointer, None)
framePointer = Register(RegisterTypes.framePointer, None)
returnAddress = Register(RegisterTypes.returnAddress, None)

floatTemporary = tuple(Register(RegisterTypes.floatTemporary, i) for i in range(9))
floatCompilerTemporary = tuple(Register(RegisterTypes.floatTemporary, i) for i in range(9, 11))
floatSaved = tuple(Register(RegisterTypes.floatSaved, i) for i in range(20,32))