from utils.consoleColors import yellow_text
from DataType import DataType
class Offset(DataType):
  def __init__(self, base, offset,type):
    """
    base: Variable que contiene la dirección de memoria base
    offset: variable que contiene el desplazamiento de la dirección de memoria
    Type: Tipo o tipos de datos que se encuentran en la dirección de memoria
    
    Ejemplo: 
    t0 = 0x7ffee2b8c4fc
    t1 = 4
    offset = Offset(t0, t1) = 4(0x7ffee2b8c4fc)  
    """
    self.base = base
    self.offset = offset
    self.type = type
  
  def getType(self):
    return self.type
  
  def equalsType(self, __class__):
    return self.type.equalsType(__class__)
  
  def strictEqualsType(self, __class__):
    return self.type.strictEqualsType(__class__)
  
  def __repr__(self) -> str:
    return f"Offset({str(self.base)},{self.offset})"
  
  def __str__(self) -> str:
    return f"Offset({str(self.base)},{self.offset})"