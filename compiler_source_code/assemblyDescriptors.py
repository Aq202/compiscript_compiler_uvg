from register import Register, RegisterTypes, temporary, saved, floatTemporary, floatSaved
from compoundTypes import ObjectType

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
  
  def freeRegister(self, register):

    if register not in self._registers:
      raise Exception(f"El registro {register} no existe.")
    
    self._registers[register] = set()

  def __str__(self) -> str:
    res = "\nRegister Descriptor:\n"
    for register in self._registers:
      if len(self._registers[register]) > 0:
        res += f"{register}: {self._registers[register]}\n"
        
    return res

class AddressDescriptor:
  
  def __init__(self):
    
    self._addresses = dict()
    
  def _hasRegister(self, object):
    """
    Verficar si una dirección ya tiene asignado un registro.
    """
    return any(isinstance(address, Register) for address in self._addresses.get(object, []))
  
  def _hasObjectType(self, object):
    """
    Verificar si una dirección ya tiene asignada una dirección de memoria (ObjectType)
    """
    return any(isinstance(address, ObjectType) for address in self._addresses.get(object, []))
    
    
  def insertAddress(self, object, address):
    
    if not any(object == obj for obj in self._addresses):
      self._addresses[object] = [address]
    
    elif not any(address == addr for addr in self._addresses[object]):
      
      if isinstance(address, Register):
        # Validar que no tenga un registro asignado
        if self._hasRegister(object):
          raise Exception(f"La dirección {object} ya tiene asignado un registro.")
        
        # Si es un registro añadir al inicio
        self._addresses[object].insert(0, address)
        return
      
      # Verificar que no tenga una dirección de memoria asignada (objectType)
      if self._hasObjectType(object):
        raise Exception(f"La dirección {object} ya tiene asignada una dirección de memoria.")
      
      self._addresses[object].append(address)

  def replaceAddress(self, object, address):
    self._addresses[object] = [address]
      
  def removeAddress(self, object, address):
    
    if any(address == addr for addr in self._addresses[object]):
      self._addresses[object].remove(address)
    
    if len(self._addresses[object]) == 0:
      del self._addresses[object]
      
  def getAddress(self, object):
    
    if not any(object == obj for obj in self._addresses) or len(self._addresses[object]) == 0:
      return None
    
    addresses = self._addresses[object]
    return addresses[0]
  
  def __str__(self) -> str:
    return "\nAddress Descriptor:\n" +  str(self._addresses)
  
  def __repr__(self) -> str:
    return "\nAddress Descriptor:\n" +  str(self._addresses)
