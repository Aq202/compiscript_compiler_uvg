from utils.consoleColors import yellow_text
class Offset:
  def __init__(self, base, offset):
    """
    base: Variable que contiene la dirección de memoria base
    offset: variable que contiene el desplazamiento de la dirección de memoria
    
    Ejemplo: 
    t0 = 0x7ffee2b8c4fc
    t1 = 4
    offset = Offset(t0, t1) = 4(0x7ffee2b8c4fc)  
    """
    self.base = base
    self.offset = offset
    
  def __repr__(self) -> str:
    return f"{self.base}{yellow_text('[')}{yellow_text(self.offset)}{yellow_text(']')}"