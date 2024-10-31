from register import Register, RegisterTypes, temporary, saved, floatTemporary, floatSaved

class RegisterDescriptor:

  def __init__(self):
    
    self._registers = dict()
    
    for register in temporary + saved + floatTemporary + floatSaved:
      self._registers[register] = set()
  
  def getRegister(self, register):
    
    if register not in self.resisters:
      raise Exception(f"El registro {register} no existe.")
    
    return self._registers[register]

  def saveValueInRegister(self, register, value):
    
    if register not in self._registers:
      raise Exception(f"El registro {register} no existe.")
    
    self._registers[register].add(value)
    
  def replaceValueInRegister(self, register, value):
      
      if register not in self._registers:
        raise Exception(f"El registro {register} no existe.")
      
      self._registers[register] = {value}
    
  def removeValueFromRegister(self, register, value):
    
    if register not in self._registers:
      raise Exception(f"El registro {register} no existe.")
    
    self._registers[register].remove(value)

  def getFreeRegisters(self):
    
    freeRegisters = []
    for register in self._registers:
      if len(self._registers[register]) == 0:
        freeRegisters.append(register)
    
    return freeRegisters
  
  def getRegistersByType(self, type):
    registers = dict()
    
    for register in self._registers:
      if register.type == type:
        registers[register] = self._registers[register]
    return registers


class AddressDescriptor:
  
  def __init__(self):
    
    self._addresses = dict()
    
  def insertAddress(self, object, address):
    
    if object not in self._addresses:
      self._addresses[object] = [address]
    elif address not in self._addresses[object]:
      
      if isinstance(address, Register):
        # Si es un registro añadir al inicio
        self._addresses[object].insert(0, address)
        return
      
      self._addresses[object].append(address)

  def replaceAddress(self, object, address):
      self._addresses[object] = [address]
      
  def removeAddress(self, object, address):
        
    self._addresses[object].remove(address)
    
    if len(self._addresses[object]) == 0:
      del self._addresses[object]
      
  def getAddress(self, object):
    
    if object not in self._addresses or len(self._addresses[object]) == 0:
      return None
    
    addresses = self._addresses[object]
    return addresses[0]
    