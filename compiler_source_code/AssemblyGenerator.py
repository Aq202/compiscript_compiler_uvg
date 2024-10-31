from assemblyDescriptors import RegisterDescriptor, AddressDescriptor
from register import RegisterTypes, Register, compilerTemporary as compTempReg, floatCompilerTemporary
from compoundTypes import ObjectType
from IntermediateCodeTokens import STATIC_POINTER, STORE, PRINT_INT, PRINT_FLOAT
from IntermediateCodeInstruction import SingleInstruction
from primitiveTypes import FloatType, IntType
from utils.decimalToIEEE754 import decimal_to_ieee754


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
  
  def getRegister(self, objectToSave=None, useTemp=False, useFloat=False, useFloatTemp=False):
    """
    Obtiene un registro disponible o adecuado para guardar el objeto.
    @param objectToSave: El objeto que se quiere guardar en un registro.
    @param useTemp: Si se debe buscar un registro temporal $t0 - t7.
    @param useFloat: Si se debe buscar un registro flotante $f0 - f29.
    
    @return: El registro disponible o adecuado para guardar el objeto.
    """
    
    # Si el objeto a guardar ya está en un registro, retornarlo
    prevAddr = self.addressDescriptor.getAddress(objectToSave)
    if len(prevAddr) > 0 and isinstance(prevAddr[0], Register):
      return prevAddr[0]
    
    freeRegisters = list(self.registerDescriptor.getFreeRegisters())
    
    # Filtrar registros que no se pueden usar
    registerType = RegisterTypes.floatTemporary if useFloatTemp else \
      RegisterTypes.floatSaved if useFloat else RegisterTypes.temporary if useTemp else RegisterTypes.saved
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
      
      # Obtener dirección de memoria para guardar el valor (en el heap)
      self.assemblyCode.append(f"lw {compTempReg[0]}, {objectOffset}({objectBasePointer})")
      self.assemblyCode.append(f"sw {minRegister}, 0({compTempReg[0]})")
      
      # Actualizar descriptores
      self.registerDescriptor.removeValueFromRegister(register=minRegister, value=object)
      self.addressDescriptor.removeAddress(object, address=minRegister)
      self.addressDescriptor.insertAddress(object, address=object)
      
    return minRegister
    
  
  def generateInitCode(self):
    
    self.assemblyCode.append(".text")
    self.assemblyCode.append(".globl main")
    self.assemblyCode.append("main:")
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
      
      elif instruction.operator == PRINT_INT:
        self.translateIntPrint(instruction)
        return
      
      elif instruction.operator == PRINT_FLOAT:
        self.translateFloatPrint(instruction)
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
        
    if isinstance(valueType, IntType):
      # Asignación de número
      memoryAddressReg = self.heapAllocate(intSize)
      
      # Guardar el valor en memoria
      self.assemblyCode.append(f"li {compTempReg[0]}, {value}")
      self.assemblyCode.append(f"sw {compTempReg[0]}, 0({memoryAddressReg})")
      
      # Guardar en registro el valor final
      register = self.getRegister(objectToSave=destination)
      self.assemblyCode.append(f"move {register}, {compTempReg[0]}")

      # Guardar en descriptores que la variable está en el registro
      self.registerDescriptor.saveValueInRegister(register, destination)
      self.addressDescriptor.insertAddress(destination, register)
    
    elif isinstance(valueType, FloatType):
      # Asignación de número
      memoryAddressReg = self.heapAllocate(floatSize)
      
      # Guardar el valor en memoria
      self.assemblyCode.append(f"li {compTempReg[0]}, {decimal_to_ieee754(value)}")
      self.assemblyCode.append(f"sw {compTempReg[0]}, 0({memoryAddressReg})")
      
      register = self.getRegister(objectToSave=destination, useFloat=True)
      self.assemblyCode.append(f"l.s {register}, 0({memoryAddressReg})")
      
      # Guardar en descriptores que la variable está en el registro
      self.registerDescriptor.saveValueInRegister(register, destination)
      self.addressDescriptor.insertAddress(destination, register)
      
      
      
      
  def translateIntPrint(self, instruction):
    
    value = instruction.arg1
    
    # Obtener ubicación más reciente    
    address = self.addressDescriptor.getAddress(value)
    
    if isinstance(address, Register):
      # El valor está en un registro
      self.assemblyCode.append(f"move $a0, {address}")
    
    else:
      # Obtener dirección del heap y luego obtener el valor guardado
      self.assemblyCode.append(f"lw {compTempReg[0]}, 0({self.getBasePointer(address)})")
      self.assemblyCode.append(f"lw $a0, 0({compTempReg[0]})")
        
    self.assemblyCode.append(f"li $v0, 1")
    self.assemblyCode.append("syscall")
    
    # Imprimir salto de línea
    self.assemblyCode.append("li $v0, 11")
    self.assemblyCode.append("li $a0, 10")
    self.assemblyCode.append("syscall")
    
  def translateFloatPrint(self, instruction):
    
    value = instruction.arg1
    
    # Obtener ubicación más reciente    
    address = self.addressDescriptor.getAddress(value)
    
    if isinstance(address, Register):
      # El valor está en un registro
      self.assemblyCode.append(f"mov.s $f12, {address}")
    
    else:
      # Obtener dirección del heap y luego obtener el valor guardado
      self.assemblyCode.append(f"lw {compTempReg[0]}, 0({address})")
      self.assemblyCode.append(f"l.s $f12, 0({compTempReg[0]})")
        
    self.assemblyCode.append(f"li $v0, 2")
    self.assemblyCode.append("syscall")
    
    # Imprimir salto de línea
    self.assemblyCode.append("li $v0, 11")
    self.assemblyCode.append("li $a0, 10")
    self.assemblyCode.append("syscall")