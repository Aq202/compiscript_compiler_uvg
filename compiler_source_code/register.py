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
      return isinstance(obj, Register) and obj.type == self.type and obj.number == self.number
    return isinstance(obj, Register) and obj.type == self.type
  
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
valueReturn = tuple(Register(RegisterTypes.valueReturn, i) for i in range(1))
arguments = tuple(Register(RegisterTypes.arguments, i) for i in range(3))
temporary = tuple(Register(RegisterTypes.temporary, i) for i in range(7))
saved = tuple(Register(RegisterTypes.saved, i) for i in range(7))
compilerTemporary = tuple(Register(RegisterTypes.temporary, i) for i in range(8,10))
reservedCompilerTemporary = (Register(RegisterTypes.arguments, 3),Register(RegisterTypes.saved, 7), Register(RegisterTypes.temporary, 7))
globalPointer = Register(RegisterTypes.globalPointer, None)
stackPointer = Register(RegisterTypes.stackPointer, None)
framePointer = Register(RegisterTypes.framePointer, None)
returnAddress = Register(RegisterTypes.returnAddress, None)

floatTemporary = tuple(Register(RegisterTypes.floatTemporary, i) for i in range(9))
floatCompilerTemporary = tuple(Register(RegisterTypes.floatTemporary, i) for i in range(9, 11))
floatSaved = tuple(Register(RegisterTypes.floatSaved, i) for i in range(20,32))
floatArguments = tuple(Register(RegisterTypes.floatTemporary, i) for i in range(12, 16))