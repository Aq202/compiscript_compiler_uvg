from assemblyDescriptors import RegisterDescriptor, AddressDescriptor
from register import RegisterTypes, Register, compilerTemporary, floatCompilerTemporary
from compoundTypes import ObjectType
from IntermediateCodeTokens import STATIC_POINTER, STORE, PRINT_INT, PRINT_FLOAT, PRINT_STR, PLUS, MINUS, MULTIPLY, DIVIDE, MOD, ASSIGN, NEG, EQUAL, NOT_EQUAL, LESS, LESS_EQUAL, GREATER, GREATER_EQUAL, GOTO, LABEL, STRICT_ASSIGN, CONCAT
from IntermediateCodeInstruction import SingleInstruction, ConditionalInstruction
from primitiveTypes import FloatType, IntType, StringType, BoolType
from utils.decimalToIEEE754 import decimal_to_ieee754
from utils.consoleColors import yellow_text
from utils.getUniqueId import getUniqueId

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
      return prevAddr
    
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
      
      elif instruction.operator == STRICT_ASSIGN:
        self.translateStrictAssignmentInstruction(instruction)
        return
      elif instruction.operator == NEG:
        self.translateNegativeOperation(instruction)
        return
      
      elif instruction.operator == PRINT_STR:
        self.translateStringPrint(instruction)
        return

      elif instruction.operator in (EQUAL, NOT_EQUAL, LESS, LESS_EQUAL, GREATER, GREATER_EQUAL):
        if not instruction.arg1.strictEqualsType(StringType):
          self.translateSimpleComparisonOperation(instruction)
        else:
          self.translateStringComparisonOperation(instruction)
        return

      elif instruction.operator == GOTO:
        self.translateJumpInstruction(instruction)
        return
      
      elif instruction.operator == LABEL:
        self.translateLabelInstruction(instruction)
        return
      
      elif instruction.operator == CONCAT:
        self.translateConcatOperation(instruction)
        return

    elif isinstance(instruction, ConditionalInstruction):
      self.translateConditionalJumpInstruction(instruction)
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
    
    if valueType.equalsType((IntType, BoolType)):
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
      
      # Guardar en memoria estática la dirección del valor en el heap
      self.assemblyCode.append(f"sw {register}, {destination.offset}({self.getBasePointer(destination)})")
      
      # Actualizar descriptores
      self.registerDescriptor.saveValueInRegister(register, value=destination)
      self.addressDescriptor.insertAddress(object=destination, address=register)
      self.addressDescriptor.insertAddress(object=destination, address=destination)
      
      
      
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
    loopLabel = f"print_string_{getUniqueId()}"
    endLabel = f"end_print_string_{getUniqueId()}"
    
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
    prevResultAddr = self.addressDescriptor.getAddress(result)
    
    if isinstance(prevResultAddr, Register):
      # Si era un registro, eliminar el valor anterior de este
      self.registerDescriptor.removeValueFromRegister(register=prevResultAddr, value=result)
    
    # Actualizar en descriptores que result = value
    self.addressDescriptor.replaceAddress(object=result, address=address)
    self.registerDescriptor.saveValueInRegister(register=address, value=result)
    
  def translateStrictAssignmentInstruction(self, instruction):
    """
    A diferencia de la asignación normal, esta instrucción no realiza la asignación de forma virtual
    a través de los descriptores, sino que mueve el valor de un registro a otro.
    """
    
    value = instruction.arg1
    result = instruction.result
    
    address = self.getValueInRegister(value)
    resultAddress = self.getValueInRegister(result, ignoreRegisters=[address])
    
    self.assemblyCode.append(f"move {resultAddress}, {address}")
    
    
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
    
  def translateSimpleComparisonOperation(self, instruction):
    
    values = (instruction.arg1, instruction.arg2)
    destination = instruction.result
    operation = instruction.operator
    
    # Obtener ubicación más reciente
    
    floatOperation = values[0].strictEqualsType(FloatType) or values[1].strictEqualsType(FloatType)
    
    # Reservar ubicación en heap correspondiente al resultado
    memoryAddressReg = self.heapAllocate(intSize)
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
      EQUAL: ("seq", "c.eq.s"),
      NOT_EQUAL: ("sne","c.eq.s"),
      LESS: ("slt", "c.lt.s"),
      LESS_EQUAL: ("sle", "c.le.s"),
      GREATER: ("sgt", "c.le.s"),
      GREATER_EQUAL: ("sge","c.lt.s")
    }
    
    # Realizar la operación
    if not floatOperation:
      resultReg = self.getRegister(objectToSave=destination, ignoreRegisters=addresses)
      self.assemblyCode.append(f"{operationMap[operation][0]} {resultReg}, {addresses[0]}, {addresses[1]} # Comparación entera")
      
    else:
      # Operación float
      # Mayor, mayor o igual y no igual se invierten
      
      resultReg = self.getRegister(objectToSave=destination, ignoreRegisters=addresses) # Guarda 0 o 1
      
      invert = operation in (NOT_EQUAL, GREATER, GREATER_EQUAL)
      falseLabel = f"false_float_comp_{getUniqueId()}"
      endLabel = f"end_float_comp_{getUniqueId()}"
      
      self.assemblyCode.append(f"{operationMap[operation][1]} {addresses[0]}, {addresses[1]} # Comparación flotante")
      if not invert:
        self.assemblyCode.append(f"bc1f {falseLabel}") # Saltar si no se cumple la condición
      else:
        self.assemblyCode.append(f"bc1t {falseLabel}") # saltar si se cumple la condición (está negado)
      
      # Si se cumple la condición
      self.assemblyCode.append(f"li {resultReg}, 1")
      self.assemblyCode.append(f"j {endLabel}")
      
      # No se cumple
      self.assemblyCode.append(f"{falseLabel}:")
      self.assemblyCode.append(f"li {resultReg}, 0")
      
      # Fin
      self.assemblyCode.append(f"{endLabel}:")
      
    # Actualizar descriptores
    self.registerDescriptor.replaceValueInRegister(resultReg, destination)
    self.addressDescriptor.replaceAddress(destination, resultReg)
  
  def translateStringComparisonOperation(self, instruction):
    values = (instruction.arg1, instruction.arg2)
    destination = instruction.result
    operation = instruction.operator
    
    # Reservar ubicación en heap correspondiente al resultado
    memoryAddressReg = self.heapAllocate(intSize)
    # Guardar en memoria estática la dirección del valor en el heap
    self.assemblyCode.append(f"sw {memoryAddressReg}, {destination.offset}({self.getBasePointer(destination)})")

    # Cargar valores en registros
    addresses = [None, None]
    for i in range(2):
      addresses[i] = self.getValueInRegister(values[i], ignoreRegisters=addresses)
      
    repeatLabel = f"repeat_string_comp_{getUniqueId()}"
    equalLabel = f"equal_string_comp_{getUniqueId()}"
    endLabel = f"end_string_comp_{getUniqueId()}"
    charDiffLabel = f"char_diff_{getUniqueId()}"
    
    resultReg = self.getRegister(objectToSave=destination, ignoreRegisters=addresses)
    
    # Loop de comparación de caracteres
    self.assemblyCode.append(f"{repeatLabel}:")
        
    # Cargar byte
    for i in range(2):
      self.assemblyCode.append(f"lb {compilerTemporary[i]}, 0({addresses[i]})")
      
    self.assemblyCode.append(f"bne {compilerTemporary[0]}, {compilerTemporary[1]}, {charDiffLabel}  # Comparar bytes")
    
    # Si son iguales y llegamos al final, las cadenas son iguales
    self.assemblyCode.append(f"beqz {compilerTemporary[0]}, {equalLabel}  # Si ambos son null, son iguales")
    
    # Avanzar a siguiente char
    self.assemblyCode.append(f"addi {addresses[0]}, {addresses[0]}, 1")
    self.assemblyCode.append(f"addi {addresses[1]}, {addresses[1]}, 1")
    
    # Repetir
    self.assemblyCode.append(f"j {repeatLabel}")
    
    # Diferencia de caracteres
    self.assemblyCode.append(f"{charDiffLabel}:")
    
    if operation == EQUAL:
      # Si la operación era igual, ya que un char es distinto, result es false
      self.assemblyCode.append(f"li {resultReg}, 0")
      self.assemblyCode.append(f"j {endLabel}")
    
    elif operation == NOT_EQUAL:
      # Si la operación era no igual, ya que un char es distinto, result es true
      self.assemblyCode.append(f"li {resultReg}, 1")
      self.assemblyCode.append(f"j {endLabel}")
      
    else:

      # Calcular la diferencia entre chars
      self.assemblyCode.append(f"sub {compilerTemporary[0]}, {compilerTemporary[0]}, {compilerTemporary[1]}")
    
      if operation in (LESS, LESS_EQUAL):
        # Si la operación es menor, para ser true debe ser negativo
        self.assemblyCode.append(f"slt {resultReg}, {compilerTemporary[0]}, $zero")
      else:
        # Si la operación es mayor, para ser true debe ser positivo
        self.assemblyCode.append(f"sgt {resultReg}, {compilerTemporary[0]}, $zero")
    
    # Saltar al final
    self.assemblyCode.append(f"j {endLabel}")
    
    # Si las cadenas son iguales
    self.assemblyCode.append(f"{equalLabel}:")
    if operation in (EQUAL, LESS_EQUAL, GREATER_EQUAL):
      self.assemblyCode.append(f"li {resultReg}, 1")
    else:
      self.assemblyCode.append(f"li {resultReg}, 0")
      
    # Fin
    self.assemblyCode.append(f"{endLabel}:")
    
    # Actualizar descriptores
    self.registerDescriptor.replaceValueInRegister(resultReg, destination)
    self.addressDescriptor.replaceAddress(destination, address=resultReg)
  
  def translateConditionalJumpInstruction(self, instruction):
    
    value = instruction.arg1
    branchIfFalse = instruction.branchIfFalse
    goToLabel = instruction.goToLabel
    
    # Obtener ubicación más reciente
    address = self.getValueInRegister(value)
    
    if branchIfFalse:
      # Saltar si es falso
      self.assemblyCode.append(f"beqz {address}, {goToLabel}")
    else:
      # Saltar si es verdadero
      self.assemblyCode.append(f"bne {address}, $zero, {goToLabel}")
  
  def translateJumpInstruction(self, instruction):
    
    goToLabel = instruction.arg1
    self.assemblyCode.append(f"j {goToLabel}")
    
  def translateLabelInstruction(self, instruction):
    label = instruction.arg1
    self.assemblyCode.append(f"{label}:")
    
  def translateConcatOperation(self, instruction):
    
    values = (instruction.arg1, instruction.arg2)
    destination = instruction.result
    
    # Obtener inicio de bloques de memoria de strings
    addresses = [None, None]
    for i in range(2):
      addresses[i] = self.getValueInRegister(values[i], ignoreRegisters=addresses)
      
    # Registro que va a irse desplazando a lo largo de la palabra
    wordCopyReg = self.getRegister(objectToSave=None, useTemp=True)
    
    # Contar tamaño de strings
    self.assemblyCode.append(f"li {compilerTemporary[0]}, 0   # Contador de tamaño de ambos strings")
    for i in range(2):
      strLenLoopLabel = f"str_len_loop{i+1}_{getUniqueId()}"
      strLenEndLabel = f"str_len_end{i+1}_{getUniqueId()}"
      
      # Copiar inicio de string a temporal, para que el original no se modifique
      self.assemblyCode.append(f"move {wordCopyReg}, {addresses[i]}   # Copiar dirección de memoria del string {i+1}")
      
      self.assemblyCode.append(f"{strLenLoopLabel}:")
      # Cargar byte actual
      self.assemblyCode.append(f"lb {compilerTemporary[1]}, 0({wordCopyReg})")
      
      # Si es nulo, terminar
      self.assemblyCode.append(f"beqz {compilerTemporary[1]}, {strLenEndLabel}")
      
      # Incrementar longitud
      self.assemblyCode.append(f"addi {compilerTemporary[0]}, {compilerTemporary[0]}, 1")
      
      # Avanzar al siguiente byte
      self.assemblyCode.append(f"addi {wordCopyReg}, {wordCopyReg}, 1")
      
      # Repetir loop con string actual
      self.assemblyCode.append(f"j {strLenLoopLabel}")
      
      self.assemblyCode.append(f"{strLenEndLabel}:")
      
    # Sumar 1 por el caracter nulo
    self.assemblyCode.append(f"addi {compilerTemporary[0]}, {compilerTemporary[0]}, 1")
      
    # Reservar memoria para el nuevo string
    self.assemblyCode.append(f"li $v0, 9")
    self.assemblyCode.append(f"move $a0, {compilerTemporary[0]}   # Reservar en heap tamanio total de ambos strings")
    self.assemblyCode.append("syscall")
    
    # Guardar en registro resultante, la dirección de memoria del nuevo string
    resultAddress = self.getRegister(objectToSave=destination, ignoreRegisters=[wordCopyReg]+ addresses)
    self.assemblyCode.append(f"move {resultAddress}, $v0")
    
    # Actualizar descriptores, indicar que el inicio del string resultante está en el registro
    self.addressDescriptor.replaceAddress(destination, resultAddress)
    self.registerDescriptor.saveValueInRegister(register=resultAddress, value=destination)
    
    # Copiar inicio de strings a temporal, el cuál se irá desplazando
    self.assemblyCode.append(f"move {compilerTemporary[0]}, {resultAddress} # Copiar en temp inicio de string resultante")
      
    # Iniciar a copiar strings
    loopCopyLabels = (f"copy_string1_{getUniqueId()}", f"copy_string2_{getUniqueId()}")
    endCopyLabels = (f"end_copy_string1_{getUniqueId()}", f"end_copy_string2_{getUniqueId()}")
  
    for i in range(2):
      
      self.assemblyCode.append(f"move {wordCopyReg}, {addresses[i]}   # Copiar dirección de memoria del string {i+1}")
      self.assemblyCode.append(f"{loopCopyLabels[i]}:")
      self.assemblyCode.append(f"lb {compilerTemporary[1]}, 0({wordCopyReg}) # Cargar byte actual a copiar de string {i+1}")
      self.assemblyCode.append(f"beqz {compilerTemporary[1]}, {endCopyLabels[i]}  # Si es nulo, terminar string {i+1}")
      self.assemblyCode.append(f"sb {compilerTemporary[1]}, 0({compilerTemporary[0]}) # Copiar byte a string resultante")
      self.assemblyCode.append(f"addi {wordCopyReg}, {wordCopyReg}, 1")
      self.assemblyCode.append(f"addi {compilerTemporary[0]}, {compilerTemporary[0]}, 1")
      self.assemblyCode.append(f"j {loopCopyLabels[i]}   # continuar copiando string {i+1}")
      self.assemblyCode.append(f"{endCopyLabels[i]}:  # Fin de copia de string {i+1}")
    
    # Agregar caracter nulo al final
    self.assemblyCode.append(f"sb $zero, 0({compilerTemporary[0]})")
    