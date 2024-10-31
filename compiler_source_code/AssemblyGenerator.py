from assemblyDescriptors import RegisterDescriptor, AddressDescriptor
from register import RegisterTypes, Register
from compoundTypes import ObjectType
from IntermediateCodeTokens import STATIC_POINTER, STORE
from IntermediateCodeInstruction import SingleInstruction
from primitiveTypes import NumberType, IntType

intSize = 4
floatSize = 4
stringSize = 255


class AssemblyGenerator:
  
  def __init__(self, code) -> None:
    self.registerDescriptor = RegisterDescriptor()
    self.addressDescriptor = AddressDescriptor()
    self.assemblyCode = []
    
    self.generateInitCode()
    
    for instruction in code:
      self.translateInstruction(instruction)
    
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
    registers = self.registerDescriptor.getRegistersByType(registerType)
    minRegister = None
    minCount = float("inf")
    for register in registers:
      if len(registers[register]) < minCount:
        minCount = len(registers[register])
        minRegister = register
    
    # Guardar el valor actual del registro menos usado
    for object in tuple(registers[minRegister]):

      # Guardar valor de registro en memoria
      objectBasePointer = self.getBasePointer(object)
      objectOffset = object.offset
      self.assemblyCode.append(f"sw {minRegister}, {objectOffset}({objectBasePointer})")
      
      # Actualizar descriptores
      self.registerDescriptor.removeValueFromRegister(register=minRegister, value=object)
      self.addressDescriptor.removeAddress(object, address=minRegister)
      self.addressDescriptor.insertAddress(object, address=object)
      
    return minRegister
    
  
  def generateInitCode(self):
    
    self.assemblyCode.append(".text")
    self.assemblyCode.append(".global main")
    self.assemblyCode.append(".main:")
    self.assemblyCode.append("li $gp, 0x10000000") # cargar dirección de gp
    
  def generateProgramExitCode(self):
    
    self.assemblyCode.append("li $v0, 10")
    self.assemblyCode.append("syscall")
    
  def getBasePointer(self, object):
    """
    Devuelve el puntero o registro (como texto) sobre el cual se debe hacer el desplazamiento (offset).
    En el caso de que se requieran operaciones extra para obtener la dirección de memoria correspondiente
    (por ejemplo, desplazarse en un registro de activación), los agrega al código assembly.
    
    Precación! Ejecutar esta función antes de realizar cada operación que haga referencia al 
    base pointer de un objeto, no se garantiza que el valor retornado permanezca fijo.
    
    @param object: El objeto del cual se quiere obtener el base pointer.
    """
    
    if isinstance(object, ObjectType):
      # Es una variable
      
      if object.baseType == STATIC_POINTER:
        return "$gp"
    
    raise Exception("No se puede obtener el base pointer de este objeto.", str(object))
  
  
  def translateInstruction(self, instruction):
    
    print(type(instruction), instruction.operator)
    if isinstance(instruction, SingleInstruction):
      
      if instruction.operator == STORE:
        # Asignación
        self.translateValueStore(instruction)
        return
    
    raise NotImplementedError("Instrucción no soportada.", str(instruction))
  
  def heapAllocate(self, size):
    """
    Reserva size cantidad de bytes en memoria dinámica y retorna (en texto) el registro que contiene la dirección.
    """
    self.assemblyCode.append(f"li $v0, 9")
    self.assemblyCode.append(f"li $a0, {size}")
    self.assemblyCode.append("syscall")
    
    return "$v0"
    
  def translateValueStore(self, instruction):
    
    destination = instruction.result
    value = instruction.arg1.value
    valueType = instruction.arg1.type
    
    destBasePointer = self.getBasePointer(destination)
    
    if isinstance(valueType, IntType):
      # Asignación de número
      memoryAddressReg = self.heapAllocate(intSize)
      
      # Guardar el valor en memoria
      self.assemblyCode.append(f"li $t8, {value}")
      self.assemblyCode.append(f"sw $t8, 0({memoryAddressReg})")
      
      
      register = self.getRegister(objectToSave=destination)
      self.assemblyCode.append(f"move {register}, {memoryAddressReg}")
      
      # Guardar en descriptores que la variable está en el registro
      self.registerDescriptor.saveValueInRegister(register, destination)
      self.addressDescriptor.insertAddress(destination, register)