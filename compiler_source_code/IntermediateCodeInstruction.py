import copy
from compoundTypes import ObjectType, FunctionType
from Offset import Offset

def format(value):
  """
  Formatear el valor para que sea legible en el código intermedio.
  """
  if isinstance(value, ObjectType):
    # Variable, devolver desplazamiento
    return f"BP[{value.offset}] : {value.type}"
  
  if isinstance(value, FunctionType):
    # Función, devolver nombre
    return value.getUniqueName()
  
  if isinstance(value, Offset):
    return f"{format(value.base)}[{format(value.offset)}]"

  return value

class Instruction():
  
  def __init__(self, nextInstruction) -> None:
    self.nextInstruction = nextInstruction
  
  def concat(self, instruction):
    """
    Concatenar instrucción hasta el final de la cadena.
    """
    if instruction == None or (isinstance(instruction, EmptyInstruction) and instruction.nextInstruction == None):
      return
    
    currentInstruction = self
    while currentInstruction.nextInstruction != None:
      currentInstruction = currentInstruction.nextInstruction
    
    currentInstruction.nextInstruction = instruction
  
  def getFullCode(self):
    """
    Obtener el código de todas las instrucciones concatenadas.
    """
    currentInstruction = self
    code = ""
    while currentInstruction != None:
      if not isinstance(currentInstruction, EmptyInstruction):
        code += str(currentInstruction) + "\n"
      currentInstruction = currentInstruction.nextInstruction
    
    return code
  
  def copyInstructions(self):
    """
    Copiar todas las instrucciones.
    """
    currentInstruction = self
    newInstruction = None
    while currentInstruction != None:
      if newInstruction == None:
        newInstruction = copy.copy(currentInstruction)
      else:
        newInstruction.concat(copy.copy(currentInstruction))
      currentInstruction = currentInstruction.nextInstruction
    
    return newInstruction
  
class EmptyInstruction(Instruction):
  def __init__(self, nextInstruction=None) -> None:
    super().__init__(nextInstruction)

class SingleInstruction(Instruction):
  def __init__(self, operator=None, arg1=None, arg2=None, result=None, nextInstruction=None, operatorFirst=False):
    super().__init__(nextInstruction)
    
    self.operator = operator
    self.arg1 = arg1
    self.arg2 = arg2
    self.result = result
    self.operatorFirst = operatorFirst
  
  def __str__(self):
    if self.result and self.operator and self.arg1 and self.arg2:
      return f"{format(self.result)} = {format(self.arg1)} {self.operator} {format(self.arg2)}"
    
    if self. result and self.operator and self.arg1:
      return f"{format(self.result)} = {self.operator} {format(self.arg1)}"
    
    if self.result and self.arg1:
      return f"{format(self.result)} = {format(self.arg1)}"
    
    if self.operator and self.arg1 and self.arg2:
      if self.operatorFirst:
        return f"{self.operator} {format(self.arg1)} {format(self.arg2)}"
      return f"{format(self.arg1)} {self.operator} {format(self.arg2)}"
    
    if self.operator and self.arg1:
      return f"{self.operator} {format(self.arg1)}"
    
    if self.operator and self.result and not self.arg1 and not self.arg2:
      return f"{format(self.result)} = {self.operator}"
    
    raise Exception("Single instruction no válida para imprimir")
class ConditionalInstruction(Instruction):
  def __init__(self, arg1, operator, arg2, goToLabel, nextInstruction=None):
    """
    Instrucción de salto condicional.
    IF arg1 operator arg2 GOTO goToLabel
    Ejemplo:
    IF a == b GOTO L1
    """
    super().__init__(nextInstruction)
    
    self.arg1 = arg1
    self.operator = operator
    self.arg2 = arg2
    self.goToLabel = goToLabel
  
  def __str__(self):
    return f"if {format(self.arg1)} {self.operator} {format(self.arg2)} goto {self.goToLabel}"