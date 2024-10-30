from assemblyDescriptors import RegisterDescriptor, AddressDescriptor
from register import RegisterTypes, Register

class AssemblyGenerator:
  
  def __init__(self, code) -> None:
    self.registerDescriptor = RegisterDescriptor()
    self.addressDescriptor = AddressDescriptor()
    self.assemblyCode = []
    
    self.generateInitCode()
    
    
    self.generateProgramExitCode()
  
  def getCode(self):
    return self.assemblyCode
  
  def getRegister(self, objectToSave=None, useTemp=False, useFloat=False):
    
    # Si el objeto a guardar ya está en un registro, retornarlo
    prevAddr = self.addressDescriptor.getAddress(objectToSave)
    if len(prevAddr) > 0 and isinstance(prevAddr[0], Register):
      return prevAddr[0]
    
    
    
    freeRegisters = list(self.registerDescriptor.getFreeRegisters())
    
    # Filtrar registros que no se pueden usar
    registerType = RegisterTypes.float if useFloat else RegisterTypes.temporary if useTemp else RegisterTypes.saved
    freeRegisters = [r for r in freeRegisters if r.type == registerType]
    
    if len(freeRegisters) > 0:
      return freeRegisters[0]
    
    # No hay registros libres, obtener el menos usado
    raise NotImplementedError("No hay registros libres.")
    
  
  def generateInitCode(self):
    
    self.assemblyCode.append(".text")
    self.assemblyCode.append(".global main")
    self.assemblyCode.append(".main:")
    self.assemblyCode.append("li $gp, 0x10000000") # cargar dirección de gp
    
  def generateProgramExitCode(self):
    
    self.assemblyCode.append("li $v0, 10")
    self.assemblyCode.append("syscall")