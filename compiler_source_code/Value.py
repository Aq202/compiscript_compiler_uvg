class Value:
  
  def __init__(self, value, type) -> None:
    self.value = value
    self.type = type
    
  def getValue(self):
    return self.value
  
  def getType(self):
    return self.type
  
  def __repr__(self) -> str:
    return f"{self.value} : {self.type}"