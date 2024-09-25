class QuadrupleRow:
  def __init__(self, operator, arg1, arg2, result):
    self.operator = operator
    self.arg1 = arg1
    self.arg2 = arg2
    self.result = result

  def __str__(self):
    if self.result and self.operator and self.arg1 and self.arg2:
      return f"{self.result.name} = {self.arg1} {self.operator} {self.arg2}"
    
    if self. result and self.operator and self.arg1:
      return f"{self.result.name} = {self.operator} {self.arg1}"
    
    if self.result and self.arg1:
      return f"{self.result.name} = {self.arg1}"
    
    if self.operator and self.arg1 and self.arg2:
      return f"{self.arg1} {self.operator} {self.arg2}"
    
    if self.operator and self.arg1:
      return f"{self.operator} {self.arg1}"
  


class IntermediateCodeQuadruple:
  
  def __init__(self) -> None:
    self.code = []
    
  def add(self, operator=None, arg1=None, arg2=None, result=None):
    
    self.code.append(QuadrupleRow(operator, arg1, arg2, result))
    
  def __repr__(self):
    return "\n".join([str(row) for row in self.code])