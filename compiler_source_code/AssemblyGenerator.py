from assemblyDescriptors import RegisterDescriptor, AddressDescriptor
from register import RegisterTypes, Register, compilerTemporary, floatCompilerTemporary
from compoundTypes import ObjectType
from IntermediateCodeTokens import STATIC_POINTER, STORE, PRINT_INT, PRINT_FLOAT, PRINT_STR, PLUS, MINUS, MULTIPLY, DIVIDE, MOD, ASSIGN, NEG
from IntermediateCodeInstruction import SingleInstruction
from primitiveTypes import FloatType, IntType, StringType
from utils.decimalToIEEE754 import decimal_to_ieee754
from utils.consoleColors import yellow_text
from uuid import uuid4

intSize = 4
floatSize = 4
stringSize = 255


class AssemblyGenerator:
  
  def __init__(self, code) -> None:
    self.registerDescriptor = RegisterDescriptor()
    self.addressDescriptor = AddressDescriptor()
    self.assemblyCode = []
    
    self.generateInitCode()
    
    print("\n\n Iniciando traducción...\n\n")
    for instruction in code:
      self.translateInstruction(instruction)
      print(yellow_text(instruction), "\n", self.registerDescriptor, self.addressDescriptor, "\n")
    
    self.generateProgramExitCode()
  
  def getCode(self):
    return self.assemblyCode
  
  def getRegister(self, objectToSave=None, useTemp=False, useFloat=False, useFloatTemp=False, ignoreRegisters=[]):
    """
    Obtiene un registro disponible o adecuado para guardar el objeto.
    @param objectToSave: El objeto que se quiere guardar en un registro.
    @param useTemp: Si se debe buscar un registro temporal $t0 - t7.
    @param useFloat: Si se debe buscar un registro flotante $f0 - f29.
    
    @return: El registro disponible o adecuado para guardar el objeto.
    """
    
    # Si el objeto a guardar ya está en un registro, retornarlo
    prevAddr = self.addressDescriptor.getAddress(objectToSave)
    if isinstance(prevAddr, Register):
      return prevAddr[0]
    
    freeRegisters = list(self.registerDescriptor.getFreeRegisters())
    
    # Filtrar registros que no se pueden usar
    registerType = RegisterTypes.floatTemporary if useFloatTemp else \
      RegisterTypes.floatSaved if useFloat else RegisterTypes.temporary if useTemp else RegisterTypes.saved
    freeRegisters = [r for r in freeRegisters if r.type == registerType and r not in ignoreRegisters]
    
    if len(freeRegisters) > 0:
      return freeRegisters[0]
    
    # No hay registros libres, obtener el menos usado
    registers = self.registerDescriptor.getRegistersByType(registerType)
    minRegister = None
    minCount = float("inf")
    for register in registers:
      if len(registers[register]) < minCount and register not in ignoreRegisters:
        minCount = len(registers[register])
        minRegister = register
    
    # Guardar el valor actual del registro menos usado
    for object in tuple(registers[minRegister]):

      # Guardar valor de registro en memoria
      objectBasePointer = self.getBasePointer(object)
      objectOffset = object.offset
      
      if object.equalsType(FloatType) or object.equalsType(IntType):
        # Obtener dirección de memoria para guardar el valor (en el heap)
        self.assemblyCode.append(f"lw {compilerTemporary[0]}, {objectOffset}({objectBasePointer})")
        
        if object.strictEqualsType(FloatType):
          self.assemblyCode.append(f"s.s {minRegister}, 0({compilerTemporary[0]})")
        else:
          self.assemblyCode.append(f"sw {minRegister}, 0({compilerTemporary[0]})")
      
      elif object.strictEqualsType(StringType):
        # Lo que se guarda en el registro, es el inicio del bloque de memoria de la cadena
        # Guardar en memoria estática dicha dirección
        self.assemblyCode.append(f"sw {minRegister}, {objectOffset}({objectBasePointer})")
      
      # Actualizar descriptores
      self.registerDescriptor.removeValueFromRegister(register=minRegister, value=object)
      self.addressDescriptor.removeAddress(object, address=minRegister)
      self.addressDescriptor.insertAddress(object, address=object)
      
    return minRegister
    
  
  def generateInitCode(self):
    
    self.assemblyCode.append(".text")
    self.assemblyCode.append(".globl main")
    self.assemblyCode.append("main:")
    self.assemblyCode.append("li $gp, 0x10010000") # cargar dirección de gp
    
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
  
  def getValueInRegister(self, value, ignoreRegisters=[]):
    # Obtener ubicación más reciente
    address = self.addressDescriptor.getAddress(value)
    
    if not isinstance(address, Register):
      
      # El valor no está en un registro, cargar de memoria
      if value.strictEqualsType(FloatType):
        address = self.getRegister(objectToSave=value, useFloat=True, ignoreRegisters=ignoreRegisters) # Obtener registro flotante
        # Cargar dirrección del bloque de memoria en el heap
        self.assemblyCode.append(f"lw {compilerTemporary[0]}, {value.offset}({self.getBasePointer(value)})")
        # Cargar valor final
        self.assemblyCode.append(f"l.s {address}, 0({compilerTemporary[0]})")
        
      elif value.strictEqualsType(StringType):
        
        address = self.getRegister(objectToSave=value, ignoreRegisters=ignoreRegisters) # Obtener registro entero
        # Cargar dirrección del bloque de memoria en el heap
        self.assemblyCode.append(f"lw {address}, {value.offset}({self.getBasePointer(value)})")
        
      else: # Tratar com int
        address = self.getRegister(objectToSave=value, ignoreRegisters=ignoreRegisters) # Obtener registro entero
        # Cargar dirrección del bloque de memoria en el heap
        self.assemblyCode.append(f"lw {compilerTemporary[0]}, {value.offset}({self.getBasePointer(value)})")
        # Cargar valor final
        self.assemblyCode.append(f"lw {address}, 0({compilerTemporary[0]})")
        
      # Actualizar descriptores con el valor recién cargado
      self.addressDescriptor.insertAddress(value, address)
      self.registerDescriptor.saveValueInRegister(address, value)
      
    return address
  
  def translateInstruction(self, instruction):
    
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
      
      elif instruction.operator in (PLUS, MINUS, MULTIPLY, DIVIDE, MOD):
        self.translateArithmeticOperation(instruction)
        return
      
      elif instruction.operator == ASSIGN:
        self.translateAssignmentInstruction(instruction)
        return
      
      elif instruction.operator == NEG:
        self.translateNegativeOperation(instruction)
        return
      
      elif instruction.operator == PRINT_STR:
        self.translateStringPrint(instruction)
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
      
      # Guardar en memoria estática la dirección del valor en el heap
      self.assemblyCode.append(f"sw {memoryAddressReg}, {destination.offset}({self.getBasePointer(destination)})")
      
      # Guardar en registro el valor final
      register = self.getRegister(objectToSave=destination)
      self.assemblyCode.append(f"li {register}, {value}")

      # Guardar en descriptores que la variable está en el registro
      self.registerDescriptor.replaceValueInRegister(register, destination)
      self.addressDescriptor.insertAddress(destination, register)
    
    elif isinstance(valueType, FloatType):
      # Asignación de número
      memoryAddressReg = self.heapAllocate(floatSize)
      
      # Guardar el valor en memoria
      self.assemblyCode.append(f"li {compilerTemporary[0]}, {decimal_to_ieee754(value)}")
      self.assemblyCode.append(f"sw {compilerTemporary[0]}, 0({memoryAddressReg})")
      
      register = self.getRegister(objectToSave=destination, useFloat=True)
      self.assemblyCode.append(f"l.s {register}, 0({memoryAddressReg})")
      
      # Guardar en memoria estática la dirección del valor en el heap
      self.assemblyCode.append(f"sw {memoryAddressReg}, {destination.offset}({self.getBasePointer(destination)})")
      
      # Guardar en descriptores que la variable está en el registro y en memoria
      self.registerDescriptor.replaceValueInRegister(register, destination)
      self.addressDescriptor.insertAddress(destination, register)
      self.addressDescriptor.insertAddress(destination, destination)
      
    elif valueType.strictEqualsType(StringType):      
      
      # Calcular tamaño: -2 por las comillas y + 1 por el caracter nulo
      size = len(value) - 1
      memoryAddressReg = self.heapAllocate(size)
      
      # Agregar código assembly para guardar cada caracter en memoria
      for i, char in enumerate(value[1:-1]):
        self.assemblyCode.append(f"li {compilerTemporary[0]}, {ord(char)}   # Caracter {char}")
        self.assemblyCode.append(f"sb {compilerTemporary[0]}, {i}({memoryAddressReg})")
        
      # Agregar caracter nulo al final
      self.assemblyCode.append(f"li {compilerTemporary[0]}, 0   # Caracter nulo")
      self.assemblyCode.append(f"sb {compilerTemporary[0]}, {size - 1}({memoryAddressReg})")
      
      # Guardar en registro la dirección de memoria del inicio del string
      register = self.getRegister(objectToSave=destination)
      self.assemblyCode.append(f"move {register}, {memoryAddressReg}  # Guardar dirección de memoria del string")
      
      # Actualizar descriptores
      self.registerDescriptor.saveValueInRegister(register, value=destination)
      self.addressDescriptor.insertAddress(object=destination, address=register)
      
      
      
      
  def translateIntPrint(self, instruction):
    
    value = instruction.arg1
    
    # Obtener ubicación más reciente    
    address = self.getValueInRegister(value)
    self.assemblyCode.append(f"move $a0, {address}")
    
    self.assemblyCode.append(f"li $v0, 1")
    self.assemblyCode.append("syscall")
    
    # Imprimir salto de línea
    self.assemblyCode.append("li $v0, 11")
    self.assemblyCode.append("li $a0, 10")
    self.assemblyCode.append("syscall")
    
  def translateFloatPrint(self, instruction):
    
    value = instruction.arg1
    
    # Obtener ubicación más reciente    
    address = self.getValueInRegister(value)
    self.assemblyCode.append(f"mov.s $f12, {address}")
        
    self.assemblyCode.append(f"li $v0, 2")
    self.assemblyCode.append("syscall")
    
    # Imprimir salto de línea
    self.assemblyCode.append("li $v0, 11")
    self.assemblyCode.append("li $a0, 10")
    self.assemblyCode.append("syscall")

  def translateStringPrint(self, instruction):
    
    value = instruction.arg1
    
    # Obtener ubicación de inicio de bloque de mem de string en registro
    address = self.getValueInRegister(value)
    
    # Cargar e imprimir cada caracter hasta encontrar el nulo
    id = uuid4()
    loopLabel = f"print_string"
    endLabel = f"end_print_string"
    
    self.assemblyCode.append(f"move {compilerTemporary[0]}, {address} # Guardar dirección de memoria del string")
    self.assemblyCode.append(f"{loopLabel}:   # Imprimir string")
    self.assemblyCode.append(f"lb $a0, 0({compilerTemporary[0]})")
    self.assemblyCode.append(f"beqz $a0, {endLabel}")
    self.assemblyCode.append(f"li $v0, 11")
    self.assemblyCode.append(f"syscall")
    self.assemblyCode.append(f"addi {compilerTemporary[0]}, {compilerTemporary[0]}, 1 # Siguiente caracter")
    self.assemblyCode.append(f"j {loopLabel}")
    self.assemblyCode.append(f"{endLabel}:")
    
    
  
  def translateArithmeticOperation(self, instruction):
      
      values = (instruction.arg1, instruction.arg2)
      destination = instruction.result
      operation = instruction.operator
      
      # Obtener ubicación más reciente
      
      floatOperation = operation == DIVIDE or values[0].strictEqualsType(FloatType) or values[1].strictEqualsType(FloatType)
      
      # Reservar ubicación en heap correspondiente al resultado
      size = floatSize if floatOperation else intSize
      memoryAddressReg = self.heapAllocate(size)
      # Guardar en memoria estática la dirección del valor en el heap
      self.assemblyCode.append(f"sw {memoryAddressReg}, {destination.offset}({self.getBasePointer(destination)})")
      
      
      # Cargar valores en registros
      addresses = [None, None]
      for i in range(2):
        addresses[i] = self.getValueInRegister(values[i], ignoreRegisters=addresses)
      
      # Realizar conversión de tipos si es necesario
      if floatOperation:
        
        for i in range(2):
          if not values[i].strictEqualsType(FloatType):
            
            self.assemblyCode.append(f"mtc1 {addresses[i]} {floatCompilerTemporary[i]}")
            self.assemblyCode.append(f"cvt.s.w {floatCompilerTemporary[i]}, {floatCompilerTemporary[i]}")
            addresses[i] = floatCompilerTemporary[i]
      
      operationMap = {
        PLUS: ("add", "add.s"),
        MINUS: ("sub", "sub.s"),
        MULTIPLY: ("mul", "mul.s"),
        DIVIDE: ("div", "div.s"),
        MOD: ("remu",)
      }
      
      # Realizar la operación
      if not floatOperation:
        resultReg = self.getRegister(objectToSave=destination, ignoreRegisters=addresses)
        self.assemblyCode.append(f"{operationMap[operation][0]} {resultReg}, {addresses[0]}, {addresses[1]}")
        
      elif operation != MOD:
        resultReg = self.getRegister(objectToSave=destination, useFloat=True, ignoreRegisters=addresses)
        self.assemblyCode.append(f"{operationMap[operation][1]} {resultReg}, {addresses[0]}, {addresses[1]}")
        
      else: # MOD float 
        
        modRegTemp = self.getRegister(objectToSave=None, useFloat=True, ignoreRegisters=addresses)
        # División (float)
        self.assemblyCode.append(f"div.s {modRegTemp}, {addresses[0]}, {addresses[1]}")
        # Convertir cociente a entero (truncamiento)
        self.assemblyCode.append(f"floor.w.s {modRegTemp}, {modRegTemp}")
        # Convertir a float de nuevo
        self.assemblyCode.append(f"cvt.s.w {modRegTemp}, {modRegTemp}")
        # mult parte entera * divisor
        self.assemblyCode.append(f"mul.s {modRegTemp}, {modRegTemp}, {addresses[1]}")
        # calcular modulo (dividendo - parte entera * divisor)
        resultReg = self.getRegister(objectToSave=destination, useFloat=True, ignoreRegisters=addresses)
        self.assemblyCode.append(f"sub.s {resultReg}, {addresses[0]}, {modRegTemp}")
        
      # Actualizar descriptores
      self.registerDescriptor.replaceValueInRegister(resultReg, destination)
      self.addressDescriptor.replaceAddress(destination, resultReg)
      
      
  def translateAssignmentInstruction(self, instruction):
    
    value = instruction.arg1
    result = instruction.result
    
    address = self.getValueInRegister(value)
    
    # Actualizar en descriptores que result = value
    self.addressDescriptor.replaceAddress(object=result, address=address)
    self.registerDescriptor.saveValueInRegister(register=address, value=result)
    
  def translateNegativeOperation(self, instruction):
    
    value = instruction.arg1
    destination = instruction.result
    
    # Obtener ubicación más reciente
    address = self.getValueInRegister(value)
    
    floatOperation = value.strictEqualsType(FloatType)
    
    # Reservar ubicación en heap correspondiente al resultado
    size = floatSize if floatOperation else intSize
    memoryAddressReg = self.heapAllocate(size)
    # Guardar en memoria estática la dirección del valor en el heap
    self.assemblyCode.append(f"sw {memoryAddressReg}, {destination.offset}({self.getBasePointer(destination)})")
    
    # Realizar la operación
    if floatOperation:
      resultReg = self.getRegister(objectToSave=destination, useFloat=True, ignoreRegisters=[address])
      self.assemblyCode.append(f"neg.s {resultReg}, {address}")
    else:
      resultReg = self.getRegister(objectToSave=destination, ignoreRegisters=[address])
      self.assemblyCode.append(f"neg {resultReg}, {address}")
    
    # Actualizar descriptores
    self.registerDescriptor.replaceValueInRegister(register=resultReg, value=destination)
    self.addressDescriptor.replaceAddress(object=destination, address=resultReg)