from assemblyDescriptors import RegisterDescriptor, AddressDescriptor
from register import RegisterTypes, Register, compilerTemporary, floatCompilerTemporary
from compoundTypes import ObjectType
from IntermediateCodeTokens import STATIC_POINTER, STORE, PRINT_INT, PRINT_FLOAT, PRINT_STR, PLUS, MINUS, MULTIPLY, DIVIDE, MOD, ASSIGN, NEG, EQUAL, NOT_EQUAL, LESS, LESS_EQUAL, GREATER, GREATER_EQUAL, GOTO, LABEL, STRICT_ASSIGN, CONCAT, INT_TO_STR, FLOAT_TO_INT, NOT, REGISTER_FREE, GHOST_REGISTER_FREE
from IntermediateCodeInstruction import SingleInstruction, ConditionalInstruction
from primitiveTypes import FloatType, IntType, StringType, BoolType, NilType, NumberType
from utils.decimalToIEEE754 import decimal_to_ieee754
from utils.consoleColors import yellow_text
from utils.getUniqueId import getUniqueId

intSize = 4
floatSize = 4
stringSize = 255
intAsStrSize = 11 # Tamaño máximo de un entero en string (+ null)

class AssemblyGenerator:
  
  def __init__(self, code) -> None:
    self.registerDescriptor = RegisterDescriptor()
    self.addressDescriptor = AddressDescriptor()
    self.assemblyCode = []
    self.functionsCode = []
    
    # Nombre de funciones del compilador
    self.autoNumberMemoryAlloc = f"auto_number_memory_alloc_{getUniqueId()}"
    
    self.generateInitCode()
    
    print("\n\n Iniciando traducción...\n\n")
    for instruction in code:
      self.addAssemblyCode(f"nop # INSTRUCTION {instruction}")
      self.translateInstruction(instruction)
      #print(yellow_text(instruction), "\n", self.registerDescriptor, self.addressDescriptor, "\n")
    
    self.generateProgramExitCode()
    
    # Agregar funciones propias del compilador
    
    # Crear direcciones de memoria en el heap para almacenar números si no existen
    self.addAutoNumberMemoryAllocFunction()
    
    self.assemblyCode += self.functionsCode
  
  def addAssemblyCode(self, code):
    self.assemblyCode.append(code)
    line = len(self.assemblyCode)
    return line
  
  def getCode(self):
    return self.assemblyCode
  
  def addAutoNumberMemoryAllocFunction(self):
    """
    Agregar función que verifica si en una dirección de memoria dada, existe la dirección de memoria
    del inicio de otro bloque de memoria (en el heap) para almacenar números. 
    Si no existe, lo crea.
    a0: contiene la dirección de memoria a verificar en el heap (valor guardado en a1). Si no existe es cero.
    a1: Contiene la dirección de memoria de la memoria estática. Equivalente a offset(base_pointer).
    a2: size del bloque de memoria a crear.
    v0: dirección de memoria del bloque de memoria creado (o el ya existente).
    """
    
    
    functionLabel = self.autoNumberMemoryAlloc
    skipMemoryAllocLabel = f"skip_auto_number_memory_alloc_{getUniqueId()}"
    
    self.addAssemblyCode(f".text")
    self.addAssemblyCode(f".globl {functionLabel}")
    self.addAssemblyCode(f"{functionLabel}:")
    
    # Verificar si existe un bloque de memoria en el heap, si no crearlo antes de leer
    self.addAssemblyCode(f"bne $a0, $zero, {skipMemoryAllocLabel} # Si no es cero, ya hay memoria asignada")
        
    # Reservar memoria en el heap
    self.addAssemblyCode(f"li $v0, 9")
    self.addAssemblyCode(f"move $a0, $a2")
    self.addAssemblyCode("syscall")
    
    # Guardar dirección de memoria en la memoria estática
    self.addAssemblyCode(f"sw $v0, 0($a1)")   
    
    # Return. V0 ya contiene la dirección del bloque creado en el heap
    self.addAssemblyCode(f"jr $ra")
    self.addAssemblyCode(f"nop")
    
    self.addAssemblyCode(f"{skipMemoryAllocLabel}:")
    self.addAssemblyCode(f"move $v0, $a0")
    
    # Return
    self.addAssemblyCode(f"jr $ra")
    self.addAssemblyCode(f"nop")
    
  
  
  def saveRegisterValueInMemory(self, register, object):
    """
    Guarda el valor de un registro en memoria, en la ubicación correspondiente al objeto.
    Si es un number guarda el valor del numero en el heap, es decir, objectStatic->heapAddress->storeValue.
    
    Modifica valores de $a0, $a1, $a2, $v0.
    """
    
    
    # Guardar valor de registro en memoria
    objectBasePointer = self.getBasePointer(object)
    objectOffset = object.offset
    
    if object.equalsType((IntType, BoolType, FloatType, NumberType, NilType)):
      # Obtener dirección de memoria para guardar el valor (en el heap)
      self.addAssemblyCode(f"lw $a0, {objectOffset}({objectBasePointer}) # Guardar inicio de bloque mem de heap en registro")
      
      # Llamar a función para verificar si existe un bloque de memoria en el heap, si no crearlo antes de leer
      self.addAssemblyCode(f"move $a1, {objectBasePointer}")
      self.addAssemblyCode(f"addi $a1, $a1, {objectOffset}")
      self.addAssemblyCode(f"li $a2, {floatSize if object.strictEqualsType(FloatType) else intSize}")
      self.addAssemblyCode(f"jal {self.autoNumberMemoryAlloc}")
      
      if object.strictEqualsType(FloatType):
        self.addAssemblyCode(f"s.s {register}, 0($v0)")
      else:
        self.addAssemblyCode(f"sw {register}, 0($v0)")
    
    elif object.strictEqualsType(StringType):
      # Lo que se guarda en el registro, es el inicio del bloque de memoria de la cadena
      # Guardar en memoria estática dicha dirección
      self.addAssemblyCode(f"sw {register}, {objectOffset}({objectBasePointer}) # Guardar inicio de string")
    
    
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

      self.saveRegisterValueInMemory(minRegister, object)
      
      # Actualizar descriptores
      self.registerDescriptor.removeValueFromRegister(register=minRegister, value=object)
      self.addressDescriptor.removeAddress(object, address=minRegister)
      self.addressDescriptor.insertAddress(object, address=object)
      
    return minRegister
    
  
  def generateInitCode(self):
    
    self.addAssemblyCode(".text")
    self.addAssemblyCode(".globl main")
    self.addAssemblyCode("main:")
    self.addAssemblyCode("li $gp, 0x10010000") # cargar dirección de gp
    
  def generateProgramExitCode(self):
    
    self.addAssemblyCode("li $v0, 10")
    self.addAssemblyCode("syscall")
    
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
        self.addAssemblyCode(f"lw {compilerTemporary[0]}, {value.offset}({self.getBasePointer(value)})  # cargar addr de heap de float {value}")
        # Cargar valor final
        self.addAssemblyCode(f"l.s {address}, 0({compilerTemporary[0]})")
        
      elif value.strictEqualsType(StringType):
        
        address = self.getRegister(objectToSave=value, ignoreRegisters=ignoreRegisters) # Obtener registro entero
        # Cargar dirrección del bloque de memoria en el heap
        self.addAssemblyCode(f"lw {address}, {value.offset}({self.getBasePointer(value)}) # cargar addr de heap str {value}")
        
      else: # Tratar com int
        address = self.getRegister(objectToSave=value, ignoreRegisters=ignoreRegisters) # Obtener registro entero
        # Cargar dirrección del bloque de memoria en el heap
        self.addAssemblyCode(f"lw {compilerTemporary[0]}, {value.offset}({self.getBasePointer(value)})  # cargar addr de heap int {value}")
        # Cargar valor final
        self.addAssemblyCode(f"lw {address}, 0({compilerTemporary[0]}) # NOTA")
        
      # Actualizar descriptores con el valor recién cargado
      self.addressDescriptor.insertAddress(value, address)
      self.registerDescriptor.saveValueInRegister(address, value)
      
    return address
  
  def freeAllRegisters(self, updateDescriptors=True):
    
    usedRegisters = self.registerDescriptor.getUsedRegisters()
    
    for register in usedRegisters:
      
      for object in tuple(self.registerDescriptor.getValuesInRegister(register)):
        
        self.saveRegisterValueInMemory(register, object)
        
        # Actualizar descriptores
        if updateDescriptors:
          self.registerDescriptor.removeValueFromRegister(register=register, value=object)
          self.addressDescriptor.replaceAddress(object, address=object)
  
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
      
      elif instruction.operator == INT_TO_STR:
        self.translateIntToStrOperation(instruction)
        return
      
      elif instruction.operator == FLOAT_TO_INT:
        self.translateFloatToIntOperation(instruction)
        return
      
      elif instruction.operator == NOT:
        self.translateNotOperation(instruction)
        return
      
      elif instruction.operator == REGISTER_FREE:
        self.freeAllRegisters()
        return
      
      elif instruction.operator == GHOST_REGISTER_FREE:
        self.freeAllRegisters(updateDescriptors=False)
        return

    elif isinstance(instruction, ConditionalInstruction):
      self.translateConditionalJumpInstruction(instruction)
      return
    
    raise NotImplementedError("Instrucción no soportada.", str(instruction))
  
  def heapAllocate(self, size):
    """
    Reserva size cantidad de bytes en memoria dinámica y retorna (en texto) el registro que contiene la dirección.
    """
    self.addAssemblyCode(f"li $v0, 9")
    self.addAssemblyCode(f"li $a0, {size}")
    self.addAssemblyCode("syscall")
    
    return "$v0"
    
  def translateValueStore(self, instruction):
    
    destination = instruction.result
    value = instruction.arg1.value if instruction.arg1.value != None else 0 # Considerar nil
    valueType = instruction.arg1.type
        
    if valueType.equalsType((IntType, BoolType, NilType)):
      # Asignación de número
      memoryAddressReg = self.heapAllocate(intSize)
      
      # Guardar en memoria estática la dirección del valor en el heap
      self.addAssemblyCode(f"sw {memoryAddressReg}, {destination.offset}({self.getBasePointer(destination)}) # Int store {str(destination)}")
      
      # Guardar en registro el valor final
      register = self.getRegister(objectToSave=destination)
      self.addAssemblyCode(f"li {register}, {value}")

      # Guardar en descriptores que la variable está en el registro
      self.registerDescriptor.replaceValueInRegister(register, destination)
      self.addressDescriptor.insertAddress(destination, register)
    
    elif isinstance(valueType, FloatType):
      # Asignación de número
      memoryAddressReg = self.heapAllocate(floatSize)
      
      # Mover dirección de memoria creada a registro seguro
      self.addAssemblyCode(f"move {compilerTemporary[1]}, {memoryAddressReg}")
      memoryAddressReg = compilerTemporary[1]
      
      # Guardar el valor en memoria
      self.addAssemblyCode(f"li {compilerTemporary[0]}, {decimal_to_ieee754(value)} # Float store")
      self.addAssemblyCode(f"sw {compilerTemporary[0]}, 0({memoryAddressReg})")
      
      register = self.getRegister(objectToSave=destination, useFloat=True)
      self.addAssemblyCode(f"l.s {register}, 0({memoryAddressReg})")
      
      # Guardar en memoria estática la dirección del valor en el heap
      self.addAssemblyCode(f"sw {memoryAddressReg}, {destination.offset}({self.getBasePointer(destination)})")
      
      # Guardar en descriptores que la variable está en el registro y en memoria
      self.registerDescriptor.replaceValueInRegister(register, destination)
      self.addressDescriptor.insertAddress(destination, register)
      self.addressDescriptor.insertAddress(destination, destination)
      
    elif valueType.strictEqualsType(StringType):      
      
      # Calcular tamaño: -2 por las comillas y + 1 por el caracter nulo
      size = len(value) - 1
      memoryAddressReg = self.heapAllocate(size)
      
      # Mover dirección de memoria creada a registro seguro
      self.addAssemblyCode(f"move {compilerTemporary[1]}, {memoryAddressReg}")
      memoryAddressReg = compilerTemporary[1]
      
      # Agregar código assembly para guardar cada caracter en memoria
      for i, char in enumerate(value[1:-1]):
        self.addAssemblyCode(f"li {compilerTemporary[0]}, {ord(char)}   # Caracter {char}")
        self.addAssemblyCode(f"sb {compilerTemporary[0]}, {i}({memoryAddressReg})")
        
      # Agregar caracter nulo al final
      self.addAssemblyCode(f"li {compilerTemporary[0]}, 0   # Caracter nulo")
      self.addAssemblyCode(f"sb {compilerTemporary[0]}, {size - 1}({memoryAddressReg})")
      
      # Guardar en registro la dirección de memoria del inicio del string
      register = self.getRegister(objectToSave=destination)
      self.addAssemblyCode(f"move {register}, {memoryAddressReg}  # Guardar dirección de memoria del string")
      
      # Guardar en memoria estática la dirección del valor en el heap
      self.addAssemblyCode(f"sw {register}, {destination.offset}({self.getBasePointer(destination)})")
      
      # Actualizar descriptores
      self.registerDescriptor.saveValueInRegister(register, value=destination)
      self.addressDescriptor.insertAddress(object=destination, address=register)
      self.addressDescriptor.insertAddress(object=destination, address=destination)
      
      
      
  def translateIntPrint(self, instruction):
    
    value = instruction.arg1
    
    # Obtener ubicación más reciente    
    address = self.getValueInRegister(value)
    self.addAssemblyCode(f"move $a0, {address}")
    
    self.addAssemblyCode(f"li $v0, 1")
    self.addAssemblyCode("syscall")
    
    # Imprimir salto de línea
    self.addAssemblyCode("li $v0, 11")
    self.addAssemblyCode("li $a0, 10")
    self.addAssemblyCode("syscall")
    
  def translateFloatPrint(self, instruction):
    
    value = instruction.arg1
    
    # Obtener ubicación más reciente    
    address = self.getValueInRegister(value)
    self.addAssemblyCode(f"mov.s $f12, {address}")
        
    self.addAssemblyCode(f"li $v0, 2")
    self.addAssemblyCode("syscall")
    
    # Imprimir salto de línea
    self.addAssemblyCode("li $v0, 11")
    self.addAssemblyCode("li $a0, 10")
    self.addAssemblyCode("syscall")

  def translateStringPrint(self, instruction):
    
    value = instruction.arg1
    
    # Obtener ubicación de inicio de bloque de mem de string en registro
    address = self.getValueInRegister(value)
    
    # Cargar e imprimir cada caracter hasta encontrar el nulo
    loopLabel = f"print_string_{getUniqueId()}"
    endLabel = f"end_print_string_{getUniqueId()}"
    
    self.addAssemblyCode(f"move {compilerTemporary[0]}, {address} # Guardar dirección de memoria del string")
    self.addAssemblyCode(f"{loopLabel}:   # Imprimir string")
    self.addAssemblyCode(f"lb $a0, 0({compilerTemporary[0]})")
    self.addAssemblyCode(f"beqz $a0, {endLabel}")
    self.addAssemblyCode(f"li $v0, 11")
    self.addAssemblyCode(f"syscall")
    self.addAssemblyCode(f"addi {compilerTemporary[0]}, {compilerTemporary[0]}, 1 # Siguiente caracter")
    self.addAssemblyCode(f"j {loopLabel}")
    self.addAssemblyCode(f"{endLabel}:")
    
    # Imprimir salto de línea
    self.addAssemblyCode("li $v0, 11")
    self.addAssemblyCode("li $a0, 10")
    self.addAssemblyCode("syscall")
    
    
  
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
      self.addAssemblyCode(f"sw {memoryAddressReg}, {destination.offset}({self.getBasePointer(destination)})")
      
      
      # Cargar valores en registros
      addresses = [None, None]
      for i in range(2):
        addresses[i] = self.getValueInRegister(values[i], ignoreRegisters=addresses)
      
      # Realizar conversión de tipos si es necesario
      if floatOperation:
        
        for i in range(2):
          if not values[i].strictEqualsType(FloatType):
            
            self.addAssemblyCode(f"mtc1 {addresses[i]} {floatCompilerTemporary[i]}")
            self.addAssemblyCode(f"cvt.s.w {floatCompilerTemporary[i]}, {floatCompilerTemporary[i]}")
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
        self.addAssemblyCode(f"{operationMap[operation][0]} {resultReg}, {addresses[0]}, {addresses[1]}")
        
      elif operation != MOD:
        resultReg = self.getRegister(objectToSave=destination, useFloat=True, ignoreRegisters=addresses)
        self.addAssemblyCode(f"{operationMap[operation][1]} {resultReg}, {addresses[0]}, {addresses[1]}")
        
      else: # MOD float 
        
        modRegTemp = self.getRegister(objectToSave=None, useFloat=True, ignoreRegisters=addresses)
        # División (float)
        self.addAssemblyCode(f"div.s {modRegTemp}, {addresses[0]}, {addresses[1]}")
        # Convertir cociente a entero (truncamiento)
        self.addAssemblyCode(f"floor.w.s {modRegTemp}, {modRegTemp}")
        # Convertir a float de nuevo
        self.addAssemblyCode(f"cvt.s.w {modRegTemp}, {modRegTemp}")
        # mult parte entera * divisor
        self.addAssemblyCode(f"mul.s {modRegTemp}, {modRegTemp}, {addresses[1]}")
        # calcular modulo (dividendo - parte entera * divisor)
        resultReg = self.getRegister(objectToSave=destination, useFloat=True, ignoreRegisters=addresses)
        self.addAssemblyCode(f"sub.s {resultReg}, {addresses[0]}, {modRegTemp}")
        
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
    
    valueReg = self.getValueInRegister(value)    
    
    self.saveRegisterValueInMemory(register=valueReg, object=result)    
    
    # Eliminar valor de registro en descriptores
    resultPrevAddr = self.addressDescriptor.getAddress(result)
    if isinstance(resultPrevAddr, Register):
      # Si era un registro, eliminar el valor anterior de este
      self.registerDescriptor.removeValueFromRegister(register=resultPrevAddr, value=result)
      
    self.addressDescriptor.replaceAddress(object=result, address=result) # Eliminar registros de address de result
    
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
    self.addAssemblyCode(f"sw {memoryAddressReg}, {destination.offset}({self.getBasePointer(destination)})")
    
    # Realizar la operación
    if floatOperation:
      resultReg = self.getRegister(objectToSave=destination, useFloat=True, ignoreRegisters=[address])
      self.addAssemblyCode(f"neg.s {resultReg}, {address}")
    else:
      resultReg = self.getRegister(objectToSave=destination, ignoreRegisters=[address])
      self.addAssemblyCode(f"neg {resultReg}, {address}")
    
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
    self.addAssemblyCode(f"sw {memoryAddressReg}, {destination.offset}({self.getBasePointer(destination)})")
    
    # Cargar valores en registros
    addresses = [None, None]
    for i in range(2):
      addresses[i] = self.getValueInRegister(values[i], ignoreRegisters=addresses)
    
    # Realizar conversión de tipos si es necesario
    if floatOperation:
      
      for i in range(2):
        if not values[i].strictEqualsType(FloatType):
          
          self.addAssemblyCode(f"mtc1 {addresses[i]} {floatCompilerTemporary[i]}")
          self.addAssemblyCode(f"cvt.s.w {floatCompilerTemporary[i]}, {floatCompilerTemporary[i]}")
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
      self.addAssemblyCode(f"{operationMap[operation][0]} {resultReg}, {addresses[0]}, {addresses[1]} # Comparación entera")
      
    else:
      # Operación float
      # Mayor, mayor o igual y no igual se invierten
      
      resultReg = self.getRegister(objectToSave=destination, ignoreRegisters=addresses) # Guarda 0 o 1
      
      invert = operation in (NOT_EQUAL, GREATER, GREATER_EQUAL)
      falseLabel = f"false_float_comp_{getUniqueId()}"
      endLabel = f"end_float_comp_{getUniqueId()}"
      
      self.addAssemblyCode(f"{operationMap[operation][1]} {addresses[0]}, {addresses[1]} # Comparación flotante")
      if not invert:
        self.addAssemblyCode(f"bc1f {falseLabel}") # Saltar si no se cumple la condición
      else:
        self.addAssemblyCode(f"bc1t {falseLabel}") # saltar si se cumple la condición (está negado)
      
      # Si se cumple la condición
      self.addAssemblyCode(f"li {resultReg}, 1")
      self.addAssemblyCode(f"j {endLabel}")
      
      # No se cumple
      self.addAssemblyCode(f"{falseLabel}:")
      self.addAssemblyCode(f"li {resultReg}, 0")
      
      # Fin
      self.addAssemblyCode(f"{endLabel}:")
      
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
    self.addAssemblyCode(f"sw {memoryAddressReg}, {destination.offset}({self.getBasePointer(destination)})")

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
    self.addAssemblyCode(f"{repeatLabel}:")
        
    # Cargar byte
    for i in range(2):
      self.addAssemblyCode(f"lb {compilerTemporary[i]}, 0({addresses[i]})")
      
    self.addAssemblyCode(f"bne {compilerTemporary[0]}, {compilerTemporary[1]}, {charDiffLabel}  # Comparar bytes")
    
    # Si son iguales y llegamos al final, las cadenas son iguales
    self.addAssemblyCode(f"beqz {compilerTemporary[0]}, {equalLabel}  # Si ambos son null, son iguales")
    
    # Avanzar a siguiente char
    self.addAssemblyCode(f"addi {addresses[0]}, {addresses[0]}, 1")
    self.addAssemblyCode(f"addi {addresses[1]}, {addresses[1]}, 1")
    
    # Repetir
    self.addAssemblyCode(f"j {repeatLabel}")
    
    # Diferencia de caracteres
    self.addAssemblyCode(f"{charDiffLabel}:")
    
    if operation == EQUAL:
      # Si la operación era igual, ya que un char es distinto, result es false
      self.addAssemblyCode(f"li {resultReg}, 0")
      self.addAssemblyCode(f"j {endLabel}")
    
    elif operation == NOT_EQUAL:
      # Si la operación era no igual, ya que un char es distinto, result es true
      self.addAssemblyCode(f"li {resultReg}, 1")
      self.addAssemblyCode(f"j {endLabel}")
      
    else:

      # Calcular la diferencia entre chars
      self.addAssemblyCode(f"sub {compilerTemporary[0]}, {compilerTemporary[0]}, {compilerTemporary[1]}")
    
      if operation in (LESS, LESS_EQUAL):
        # Si la operación es menor, para ser true debe ser negativo
        self.addAssemblyCode(f"slt {resultReg}, {compilerTemporary[0]}, $zero")
      else:
        # Si la operación es mayor, para ser true debe ser positivo
        self.addAssemblyCode(f"sgt {resultReg}, {compilerTemporary[0]}, $zero")
    
    # Saltar al final
    self.addAssemblyCode(f"j {endLabel}")
    
    # Si las cadenas son iguales
    self.addAssemblyCode(f"{equalLabel}:")
    if operation in (EQUAL, LESS_EQUAL, GREATER_EQUAL):
      self.addAssemblyCode(f"li {resultReg}, 1")
    else:
      self.addAssemblyCode(f"li {resultReg}, 0")
      
    # Fin
    self.addAssemblyCode(f"{endLabel}:")
    
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
      self.addAssemblyCode(f"beqz {address}, {goToLabel}")
    else:
      # Saltar si es verdadero
      self.addAssemblyCode(f"bne {address}, $zero, {goToLabel}")
  
  def translateJumpInstruction(self, instruction):
    
    goToLabel = instruction.arg1
    self.addAssemblyCode(f"j {goToLabel}")
    
  def translateLabelInstruction(self, instruction):
    label = instruction.arg1
    self.addAssemblyCode(f"{label}:")
    
  def translateConcatOperation(self, instruction):
    
    values = (instruction.arg1, instruction.arg2)
    destination = instruction.result
    
    # Obtener inicio de bloques de memoria de strings
    addresses = [None, None]
    for i in range(2):
      addresses[i] = self.getValueInRegister(values[i], ignoreRegisters=addresses)
      
    # Registro que va a irse desplazando a lo largo de la palabra
    wordCopyReg = self.getRegister(objectToSave=None, ignoreRegisters=addresses)
    
    # Contar tamaño de strings
    self.addAssemblyCode(f"# translateConcatOperation: concatenar dos strings {addresses[0]} y {addresses[1]}")
    self.addAssemblyCode(f"li {compilerTemporary[0]}, 0   # Contador de tamaño de ambos strings")
    for i in range(2):
      strLenLoopLabel = f"str_len_loop{i+1}_{getUniqueId()}"
      strLenEndLabel = f"str_len_end{i+1}_{getUniqueId()}"
      
      # Copiar inicio de string a temporal, para que el original no se modifique
      self.addAssemblyCode(f"move {wordCopyReg}, {addresses[i]}   # Copiar dirección de memoria del string {i+1}")
      
      self.addAssemblyCode(f"{strLenLoopLabel}:")
      # Cargar byte actual
      self.addAssemblyCode(f"lb {compilerTemporary[1]}, 0({wordCopyReg})")
      
      # Si es nulo, terminar
      self.addAssemblyCode(f"beqz {compilerTemporary[1]}, {strLenEndLabel}")
      
      # Incrementar longitud
      self.addAssemblyCode(f"addi {compilerTemporary[0]}, {compilerTemporary[0]}, 1")
      
      # Avanzar al siguiente byte
      self.addAssemblyCode(f"addi {wordCopyReg}, {wordCopyReg}, 1")
      
      # Repetir loop con string actual
      self.addAssemblyCode(f"j {strLenLoopLabel}")
      
      self.addAssemblyCode(f"{strLenEndLabel}:")
      
    # Sumar 1 por el caracter nulo
    self.addAssemblyCode(f"addi {compilerTemporary[0]}, {compilerTemporary[0]}, 1")
      
    # Reservar memoria para el nuevo string
    self.addAssemblyCode(f"li $v0, 9")
    self.addAssemblyCode(f"move $a0, {compilerTemporary[0]}   # Reservar en heap tamanio total de ambos strings")
    self.addAssemblyCode("syscall")
    
    # Guardar en registro resultante, la dirección de memoria del nuevo string
    resultAddress = self.getRegister(objectToSave=destination, ignoreRegisters=[wordCopyReg]+ addresses)
    self.addAssemblyCode(f"move {resultAddress}, $v0")
    
    # Actualizar descriptores, indicar que el inicio del string resultante está en el registro
    self.addressDescriptor.replaceAddress(destination, resultAddress)
    self.registerDescriptor.saveValueInRegister(register=resultAddress, value=destination)
    
    # Copiar inicio de strings a temporal, el cuál se irá desplazando
    self.addAssemblyCode(f"move {compilerTemporary[0]}, {resultAddress} # Copiar en temp inicio de string resultante")
      
    # Iniciar a copiar strings
    loopCopyLabels = (f"copy_string1_{getUniqueId()}", f"copy_string2_{getUniqueId()}")
    endCopyLabels = (f"end_copy_string1_{getUniqueId()}", f"end_copy_string2_{getUniqueId()}")
  
    for i in range(2):
      
      self.addAssemblyCode(f"move {wordCopyReg}, {addresses[i]}   # Copiar dirección de memoria del string {i+1}")
      self.addAssemblyCode(f"{loopCopyLabels[i]}:")
      self.addAssemblyCode(f"lb {compilerTemporary[1]}, 0({wordCopyReg}) # Cargar byte actual a copiar de string {i+1}")
      self.addAssemblyCode(f"beqz {compilerTemporary[1]}, {endCopyLabels[i]}  # Si es nulo, terminar string {i+1}")
      self.addAssemblyCode(f"sb {compilerTemporary[1]}, 0({compilerTemporary[0]}) # Copiar byte a string resultante")
      self.addAssemblyCode(f"addi {wordCopyReg}, {wordCopyReg}, 1")
      self.addAssemblyCode(f"addi {compilerTemporary[0]}, {compilerTemporary[0]}, 1")
      self.addAssemblyCode(f"j {loopCopyLabels[i]}   # continuar copiando string {i+1}")
      self.addAssemblyCode(f"{endCopyLabels[i]}:  # Fin de copia de string {i+1}")
    
    # Agregar caracter nulo al final
    self.addAssemblyCode(f"sb $zero, 0({compilerTemporary[0]})")
  
  def translateIntToStrOperation(self, instruction):
    
    number = instruction.arg1
    destination = instruction.result
    
    # Reservar espacio en heap para string
    memoryAddressReg = self.heapAllocate(intAsStrSize)
    
    # Cambiar memoryAddress a registro seguro
    self.addAssemblyCode(f"move {compilerTemporary[0]}, {memoryAddressReg}")
    memoryAddressReg = compilerTemporary[0]
    
    # Guardar en registro la dirección de memoria del inicio del string
    resultAddress = self.getRegister(objectToSave=destination)
    self.addAssemblyCode(f"move {resultAddress}, {memoryAddressReg}")
    
    self.addressDescriptor.replaceAddress(destination, resultAddress)
    self.registerDescriptor.saveValueInRegister(resultAddress, value=destination)
    
    # Obtener ubicación más reciente del número
    numberAddress = self.getValueInRegister(number, ignoreRegisters=[resultAddress])
    
    # Copiar a registro temporal el número, para que se pueda operar
    numberReg = self.getRegister(objectToSave=None, ignoreRegisters=[resultAddress, numberAddress])
    self.addAssemblyCode(f"move {numberReg}, {numberAddress}  # copiar número a registro para poder modificarlo")
    
    # Guardar el divisor base 10

    handleZeroLabel = f"handle_zero_{getUniqueId()}"
    convertLoopLabel = f"convert_loop_{getUniqueId()}"
    endConvertLabel = f"end_convert_{getUniqueId()}"
    
    # Copiar inicio de string a registro temporal
    stringPointerReg = self.getRegister(objectToSave=None, ignoreRegisters=[resultAddress, numberReg])
    self.addAssemblyCode(f"move {stringPointerReg}, {resultAddress}")
    
    # Si el número es cero, convertirlo a '0' directamente
    self.addAssemblyCode(f"beqz {numberReg}, {handleZeroLabel} # Si el número es cero, convertirlo a '0'")
    
    # Guardar divisor base 10
    self.addAssemblyCode(f"li {compilerTemporary[0]}, 10")
    
    self.addAssemblyCode(f"{convertLoopLabel}:")
    
    # Obtener digito menos significativo. 
    digitReg = compilerTemporary[1]
    self.addAssemblyCode(f"div {numberReg}, {compilerTemporary[0]}  # Dividir por 10")
    self.addAssemblyCode(f"mfhi {digitReg}  # Obtener residuo (dig individual)")
    self.addAssemblyCode(f"mflo {numberReg}  # Obtener cociente (num reducido)")
    
    # Si el número es cero, no agregar char y terminar
    
    # Convertir digito a caracter
    self.addAssemblyCode(f"addi {digitReg}, {digitReg}, 48  # Convertir a caracter ASCII")
    self.addAssemblyCode(f"sb {digitReg}, 0({stringPointerReg})  # Guardar caracter en string")
    self.addAssemblyCode(f"addi {stringPointerReg}, {stringPointerReg}, 1  # Avanzar a siguiente caracter en buffer")
    
    self.addAssemblyCode(f"bne {numberReg}, $zero, {convertLoopLabel} # Si no es cero, repetir")
    
    self.addAssemblyCode(f"sb $zero, 0({stringPointerReg})  # Agregar caracter nulo al final")
    
    # Reverse loop
    
    # StringBufferReg está al final del string + 1 (caracter nulo)
    self.addAssemblyCode(f"subi {stringPointerReg}, {stringPointerReg}, 1  # Retroceder a último caracter")
    stringPointerBackwardReg = stringPointerReg # Se va a ir decrementando
    
    # Guardar otra copia del string, para recorrer de adelante hacia atras
    stringPointerForwardReg = self.getRegister(objectToSave=None, ignoreRegisters=[resultAddress, stringPointerReg, numberReg]) # Se va a ir incrementando
    self.addAssemblyCode(f"move {stringPointerForwardReg}, {resultAddress}")
    
    # Hacer reverse de la cadena
    
    reverseLoopLabel = f"reverse_loop_{getUniqueId()}"
    
    self.addAssemblyCode(f"{reverseLoopLabel}:")
    
    # Si los punteros se cruzan, terminar
    self.addAssemblyCode(f"bgeu {stringPointerForwardReg}, {stringPointerBackwardReg}, {endConvertLabel} # Si puntero forward es igual o mayor que backward, terminar")
    
    # Cargar chars
    self.addAssemblyCode(f"lb {compilerTemporary[0]}, 0({stringPointerForwardReg})  # Cargar char de adelante")
    self.addAssemblyCode(f"lb {compilerTemporary[1]}, 0({stringPointerBackwardReg})  # Cargar char de atras")
    
    # Guardar chars intercambiados
    self.addAssemblyCode(f"sb {compilerTemporary[1]}, 0({stringPointerForwardReg})  # Guardar char de adelante")
    self.addAssemblyCode(f"sb {compilerTemporary[0]}, 0({stringPointerBackwardReg})  # Guardar char de atras")
    
    # Avanzar y retroceder punteros
    self.addAssemblyCode(f"addi {stringPointerForwardReg}, {stringPointerForwardReg}, 1  # Avanzar puntero de adelante")
    self.addAssemblyCode(f"subi {stringPointerBackwardReg}, {stringPointerBackwardReg}, 1  # Retroceder puntero de atras")
    
    # Repetir loop
    self.addAssemblyCode(f"j {reverseLoopLabel}")
    
    
    
    
    
    
    
    
    # Terminar
    self.addAssemblyCode(f"j {endConvertLabel}")
    
    # Handle zero
    self.addAssemblyCode(f"{handleZeroLabel}:")
    self.addAssemblyCode(f"li {compilerTemporary[0]}, 48  # Convertir '0' a ASCII")
    self.addAssemblyCode(f"sb {compilerTemporary[0]}, 0({stringPointerReg})  # Guardar '0' en string")
    
    # Agregar nulo luego de cero
    self.addAssemblyCode(f"addi {stringPointerReg}, {stringPointerReg}, 1  # Avanzar a siguiente caracter en buffer")
    self.addAssemblyCode(f"sb $zero, 0({stringPointerReg})  # Agregar caracter nulo al final")
    
    
    self.addAssemblyCode(f"{endConvertLabel}:")
    
    
  def translateFloatToIntOperation(self, instruction):
    
    floatNumber = instruction.arg1
    destination = instruction.result
    
    # Cargar número float en registro
    floatReg = self.getValueInRegister(floatNumber)
    
    # Reservar espacio en el heap para int
    memoryAddressReg = self.heapAllocate(intSize)
    # Guardar en memoria estática la dirección del valor en el heap
    self.addAssemblyCode(f"sw {memoryAddressReg}, {destination.offset}({self.getBasePointer(destination)})")
      
    # Convertir float a int
    self.addAssemblyCode(f"cvt.w.s {floatCompilerTemporary[0]}, {floatReg}  # Convertir float a int")
    
    # Mover a registro int
    intReg = self.getRegister(objectToSave=None, useFloat=False)
    self.addAssemblyCode(f"mfc1 {intReg}, {floatCompilerTemporary[0]} # Mover int de registro f a int")
    
    # Guardar int en memoria (en el heap)
    self.addAssemblyCode(f"sw {intReg}, 0({memoryAddressReg}) # Guardar int en memoria heap")
    
    # Actualizar descriptores
    self.registerDescriptor.saveValueInRegister(register=intReg, value=destination)
    self.addressDescriptor.replaceAddress(object=destination, address=intReg)
    
  def translateNotOperation(self, instruction):
    
    value = instruction.arg1
    destination = instruction.result
    
    # Obtener valor a negar en registro
    valueReg = self.getValueInRegister(value)
    
    # Obtener ubicación de destino
    destinationReg = self.getRegister(objectToSave=destination, ignoreRegisters=[valueReg])
    
    # Negar valor
    self.addAssemblyCode(f"xori {destinationReg}, {valueReg}, 1  # Negar valor")
    
    # Actualizar descriptores para que solo destination tenga el valor
    self.registerDescriptor.replaceValueInRegister(destinationReg, destination)
    self.addressDescriptor.replaceAddress(destination, destinationReg)
    