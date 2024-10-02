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
      return f"{self.result} = {self.arg1} {self.operator} {self.arg2}"
    
    if self. result and self.operator and self.arg1:
      return f"{self.result} = {self.operator} {self.arg1}"
    
    if self.result and self.arg1:
      return f"{self.result} = {self.arg1}"
    
    if self.operator and self.arg1 and self.arg2:
      if self.operatorFirst:
        return f"{self.operator} {self.arg1} {self.arg2}"
      return f"{self.arg1} {self.operator} {self.arg2}"
    
    if self.operator and self.arg1:
      return f"{self.operator} {self.arg1}"