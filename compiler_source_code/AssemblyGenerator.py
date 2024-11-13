from assemblyDescriptors import RegisterDescriptor, AddressDescriptor
from register import RegisterTypes, Register, compilerTemporary, floatCompilerTemporary, temporary as temporaryRegisters, floatTemporary as floatTemporaryRegisters, arguments as argumentRegisters, floatArguments as floatArgumentRegisters, reservedCompilerTemporary
from compoundTypes import ObjectType, ClassSelfReferenceType, InstanceType
from IntermediateCodeTokens import STATIC_POINTER, STACK_POINTER, STORE, PRINT_INT, PRINT_FLOAT, PRINT_STR,PRINT_ANY, PLUS, MINUS, MULTIPLY, DIVIDE, MOD, ASSIGN, NEG, EQUAL, NOT_EQUAL, LESS, LESS_EQUAL, GREATER, GREATER_EQUAL, GOTO, LABEL, STRICT_ASSIGN, CONCAT, INT_TO_STR, NOT, REGISTER_FREE, GHOST_REGISTER_FREE, FUNCTION, END_FUNCTION, GET_ARG, RETURN, CALL, RETURN_VAL, PARAM, FLOAT_TO_STR, STORE_CONST, CONST_POINT_CHAR, MALLOC
from IntermediateCodeInstruction import SingleInstruction, ConditionalInstruction
from primitiveTypes import FloatType, IntType, StringType, BoolType, NilType
from utils.decimalToIEEE754 import decimal_to_ieee754
from utils.consoleColors import yellow_text
from utils.getUniqueId import getUniqueId
from Offset import Offset

numberSize = 4
stringSize = 255
intAsStrSize = 11 # Tamaño máximo de un entero en string (+ null)

intId = 1
floatId = 2
stringId = 3
objectInstanceId = 4

skipFunctionPrefix = "skip"
returnFunctionPrefix = "return"

class AssemblyGenerator:
  
  def __init__(self, code) -> None:
    self.registerDescriptor = RegisterDescriptor()
    self.addressDescriptor = AddressDescriptor()
    self.assemblyCode = []
    self.functionsCode = []
    self.constants = {} # Temporales para guardar constantes
    
    self.activeFunctions = [] # Nombre de funciones activas
    
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
    a2: tipo del número que se está guardando.
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
    self.addAssemblyCode(f"li $a0, {numberSize + 4}") # Tamaño de un número + 4 bytes para el tipo
    self.addAssemblyCode("syscall")
    
    # Guardar el tipo en el primer byte de la dirección de memoria (en el heap)
    self.addAssemblyCode(f"sb $a2, 0($v0)")
    
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
    
  def saveIntRegisterValueInMemory(self, register, object):
    """
    Guarda el valor de un registro en memoria, en la ubicación correspondiente al objeto.
    Guarda el valor del numero en el heap, es decir, objectStatic->heapAddress->storeValue.
    
    Modifica valores de $a0, $a1, $a2, $v0.
    """
    
    objectBasePointer = self.getBasePointer(object)
    objectOffset = self.getOffset(object)
    
    self.addAssemblyCode(f"lw $a0, {objectOffset}({objectBasePointer}) # Guardar int en memoria")
    
    # Llamar a función para verificar si existe un bloque de memoria en el heap, si no crearlo antes de leer
    self.addAssemblyCode(f"move $a1, {objectBasePointer}")
    self.addAssemblyCode(f"addi $a1, $a1, {objectOffset}")
    self.addAssemblyCode(f"li $a2, {intId}")
    self.addAssemblyCode(f"jal {self.autoNumberMemoryAlloc}")
    
    self.addAssemblyCode(f"sw {register}, 4($v0)")
    
  def saveFloatRegisterValueInMemory(self, register, object):
    """
    Guarda el valor de un registro en memoria, en la ubicación correspondiente al objeto.
    Guarda el valor del numero en el heap, es decir, objectStatic->heapAddress->storeValue.
    
    Modifica valores de $a0, $a1, $a2, $v0.
    """
    
    objectBasePointer = self.getBasePointer(object)
    objectOffset = self.getOffset(object)
    
    self.addAssemblyCode(f"lw $a0, {objectOffset}({objectBasePointer}) # Guardar float en memoria")
    
    # Llamar a función para verificar si existe un bloque de memoria en el heap, si no crearlo antes de leer
    self.addAssemblyCode(f"move $a1, {objectBasePointer}")
    self.addAssemblyCode(f"addi $a1, $a1, {objectOffset}")
    self.addAssemblyCode(f"li $a2, {floatId}")
    self.addAssemblyCode(f"jal {self.autoNumberMemoryAlloc}")
    
    self.addAssemblyCode(f"s.s {register}, 4($v0)")
    
  def saveHeapAddressInMemory(self, heapAddressReg, object):
    """
    Guarda el inicio de un bloque de memoria (en el heap) en la dirección correspondiente al objeto.
    """
    
    objectBasePointer = self.getBasePointer(object)
    objectOffset = self.getOffset(object)
    # Lo que se guarda en el registro, es el inicio del bloque de memoria de la cadena
    # Guardar en memoria estática dicha dirección
    self.addAssemblyCode(f"sw {heapAddressReg}, {objectOffset}({objectBasePointer}) # Guardar inicio de string")
    
  
  def saveRegisterValueInMemory(self, register, object, typeId = None):
    """
    Guarda el valor de un registro en memoria, en la ubicación correspondiente al objeto.
    Si es un number guarda el valor del numero en el heap, es decir, objectStatic->heapAddress->storeValue.
    
    Modifica valores de $a0, $a1, $a2, $v0, $f12, reservedCompilerTemporary[1].
    """
    
    if object.strictEqualsType((IntType, BoolType, NilType)) or typeId == intId:
      self.saveIntRegisterValueInMemory(register, object)
      
    elif object.strictEqualsType(FloatType) or typeId == floatId:
      self.saveFloatRegisterValueInMemory(register, object)
      
    elif object.strictEqualsType(StringType) or typeId == stringId:
      self.saveHeapAddressInMemory(register, object)
      
    elif object.strictEqualsType((ClassSelfReferenceType, InstanceType)) or typeId == objectInstanceId:
      # Guardar dirección de instancia en memoria estática
      self.saveHeapAddressInMemory(register, object)
      
    else:
      # Caso any, se debe realizar una verificación del tipo en tiempo de ejecución
      
      saveIntRegLabel = f"save_int_reg_{getUniqueId()}"
      saveFloatRegLabel = f"save_float_reg_{getUniqueId()}"
      endSaveRegLabel = f"end_save_reg_{getUniqueId()}"
      
      # Obtener dirección en el heap
      self.addAssemblyCode(f"lw $a0, {self.getOffset(object)}({self.getBasePointer(object)})")
      
      # obtener tipo
      self.addAssemblyCode(f"lb $a0, 0($a0)")
      
      # Estructura de if type == int
      self.addAssemblyCode(f"li $a1, {intId}")
      self.addAssemblyCode(f"beq $a0, $a1, {saveIntRegLabel}")
      
      # Estructura de if type == float
      self.addAssemblyCode(f"li $a1, {floatId}")
      self.addAssemblyCode(f"beq $a0, $a1, {saveFloatRegLabel}")
      
      # Por defecto es un string o instanceType
      self.saveHeapAddressInMemory(register, object)
      self.addAssemblyCode(f"j {endSaveRegLabel}")
      
      # Guardar como int
      self.addAssemblyCode(f"{saveIntRegLabel}:")
      intReg = register
      if register.type not in (RegisterTypes.temporary, RegisterTypes.saved):
        # Mover a registro entero
        intReg = reservedCompilerTemporary[1]
        self.addAssemblyCode(f"move {reservedCompilerTemporary[1]}, {register}")
      self.saveIntRegisterValueInMemory(intReg, object)
      self.addAssemblyCode(f"j {endSaveRegLabel}")
      
      # Guardar como float
      self.addAssemblyCode(f"{saveFloatRegLabel}:")
      floatReg = register
      if register.type not in (RegisterTypes.floatTemporary, RegisterTypes.floatSaved):
        # Mover a registro float: $f12
        self.addAssemblyCode(f"mtc1 {register}, $f12")
        floatReg = floatArgumentRegisters[0]
      
      self.saveFloatRegisterValueInMemory(floatReg, object)
      self.addAssemblyCode(f"j {endSaveRegLabel}")
      
      self.addAssemblyCode(f"{endSaveRegLabel}:")  
    
    
    
  def getRegister(self, objectToSave=None, useFloat=False, ignoreRegisters=[]):
    """
    Obtiene un registro disponible o adecuado para guardar el objeto.
    @param objectToSave: El objeto que se quiere guardar en un registro.
    @param useTemp: Si se debe buscar un registro temporal $t0 - t7.
    @param useFloat: Si se debe buscar un registro flotante $f0 - f29.
    
    @return: El registro disponible o adecuado para guardar el objeto.
    
    Modifica: $a0, $a1, $a2, $v0, $f12, reservedCompilerTemporary[2].
    """
    
    # Si el objeto a guardar ya está en un registro, retornarlo
    prevAddr = self.addressDescriptor.getAddress(objectToSave)
    if isinstance(prevAddr, Register):
      return prevAddr
    
    freeRegisters = list(self.registerDescriptor.getFreeRegisters())
    
    # Obligar a usar registros temporales si se encuentra dentro de una función
    useFloatTemp = len(self.activeFunctions) > 0 and useFloat
    useTemp = len(self.activeFunctions) > 0 and not useFloat
    
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
    
    Modifica: reservedCompilerTemporary[0], reservedCompilerTemporary[1] y reservedCompilerTemporary[2].
    """
    
    if isinstance(object, ObjectType):
      # Es una variable
      
      if object.baseType == STATIC_POINTER:
        return "$gp"
      elif object.baseType == STACK_POINTER:
        
        # Verificar si el functionLevel actual es el correcto
        # $fp anterior = $fp actual
        # functionLevel = $fp + 4
        
        currentFunctionLevel = object.getFunctionLevel()
        
        equalFunctionLevelLabel = f"equal_function_level_{getUniqueId()}"
        repeatFunctionLevelCheckLabel = f"repeat_function_level_check_{getUniqueId()}"
        
        self.addAssemblyCode("nop # Obtener base pointer")
        
        # Cargar functionLevel a buscar
        self.addAssemblyCode(f"li {reservedCompilerTemporary[0]}, {currentFunctionLevel} # Cargar functionLevel a buscar")
        
        # Mover $fp como punto de inicio actual
        self.addAssemblyCode(f"move {reservedCompilerTemporary[1]}, $fp # Mover $fp como punto de inicio actual")
        
        self.addAssemblyCode(f"{repeatFunctionLevelCheckLabel}:")
        
        # Cargar functionLevel actual
        self.addAssemblyCode(f"lw {reservedCompilerTemporary[2]}, 4({reservedCompilerTemporary[1]}) # Cargar functionLevel actual")
        
        # Verificar si son iguales
        self.addAssemblyCode(f"beq {reservedCompilerTemporary[0]}, {reservedCompilerTemporary[2]}, {equalFunctionLevelLabel} # Verificar si son iguales")
        
        # Si no son iguales, cargar $fp de la función anterior y repetir
        self.addAssemblyCode(f"lw {reservedCompilerTemporary[1]}, 0({reservedCompilerTemporary[1]}) # Cargar $fp de la función anterior")
        self.addAssemblyCode(f"j {repeatFunctionLevelCheckLabel}")
        
        self.addAssemblyCode(f"{equalFunctionLevelLabel}:")
        
        # Se encontró el functionLevel correcto, retornarlo como base pointer          
        return reservedCompilerTemporary[1]
    
    elif isinstance(object, Offset):
      # Se está haciendo un desplazamiento sobre un objeto en el heap
      base = object.base
      offset = object.offset
      
      self.addAssemblyCode("nop # Obtener base pointer de objeto Offset")
      # Obtiene la dirección base. 
      # Se guarda en el registro el inicio de la dirección del heap sobre la cuál se hace el desplazamiento
      self.addAssemblyCode(f"lw {reservedCompilerTemporary[0]}, {self.getOffset(base)}({self.getBasePointer(base)})")
      
      return reservedCompilerTemporary[0]
      
    
    raise Exception("No se puede obtener el base pointer de este objeto.", str(object))
  
  def getOffset(self, object):
    """
    Devuelve el desplazamiento (offset) correspondiente al objeto.
    
    Si el objeto es de tipo Offset, se devuelve cero, pues al utilizar getBasePointer se realiza
    el desplazamiento correspondiente.
    """
    
    if isinstance(object, ObjectType):
      return object.offset if object.baseType != STACK_POINTER else (object.offset * -1 - 4)
    
    if isinstance(object, Offset):
      return object.offset
    
    raise Exception("No se puede obtener el offset de este objeto.", str(object))
  
  def getValueInRegister(self, value, ignoreRegisters=[], typeId = None, updateDescriptors=True):
    # Obtener ubicación más reciente
    address = self.addressDescriptor.getAddress(value)
    
    if not isinstance(address, Register):
      
      # El valor no está en un registro, cargar de memoria
      if value.strictEqualsType(FloatType) or typeId == floatId:
        address = self.getRegister(objectToSave=value, useFloat=True, ignoreRegisters=ignoreRegisters) # Obtener registro flotante
        # Cargar dirrección del bloque de memoria en el heap
        self.addAssemblyCode(f"lw {compilerTemporary[0]}, {self.getOffset(value)}({self.getBasePointer(value)})  # cargar addr de heap de float {value}")
        # Cargar valor final (offset de 4 para omitir el byte de tipo)
        self.addAssemblyCode(f"l.s {address}, 4({compilerTemporary[0]})")
        
      elif (value.strictEqualsType(StringType) or typeId == stringId) or \
            (value.strictEqualsType((ClassSelfReferenceType, InstanceType)) or typeId == objectInstanceId):
        
        address = self.getRegister(objectToSave=value, ignoreRegisters=ignoreRegisters) # Obtener registro entero
        # Cargar dirrección del bloque de memoria en el heap
        self.addAssemblyCode(f"lw {address}, {self.getOffset(value)}({self.getBasePointer(value)}) # cargar addr de heap str {value}")
        
      else: # Tratar com int
        address = self.getRegister(objectToSave=value, ignoreRegisters=ignoreRegisters) # Obtener registro entero
        # Cargar dirrección del bloque de memoria en el heap
        self.addAssemblyCode(f"lw {compilerTemporary[0]}, {self.getOffset(value)}({self.getBasePointer(value)})  # cargar addr de heap int {value}")
        # Cargar valor final (offset de 4 para omitir el byte de tipo)
        self.addAssemblyCode(f"lw {address}, 4({compilerTemporary[0]}) # NOTA")
        
      # Actualizar descriptores con el valor recién cargado
      if updateDescriptors:
        self.addressDescriptor.insertAddress(value, address)
        self.registerDescriptor.saveValueInRegister(address, value)
      
    return address
  
  def freeAllRegisters(self, updateDescriptors=True, saveValues=True):
    """
    Liberar todos los registros, guardando los valores en memoria si se desea.
    
    Si se guarda memoria modifica: $a0, $a1, $a2, $v0, $f12, reservedCompilerTemporary[1].
    """
    
    usedRegisters = self.registerDescriptor.getUsedRegisters()
    
    for register in usedRegisters:
      
      for object in tuple(self.registerDescriptor.getValuesInRegister(register)):
        
        if saveValues:
          self.saveRegisterValueInMemory(register, object)
        
        # Actualizar descriptores
        if updateDescriptors:
          self.registerDescriptor.removeValueFromRegister(register=register, value=object)
          self.addressDescriptor.replaceAddress(object, address=object)
          
  def freeTemporaryRegisters(self):
    """
    Limpia el contenido de los registros temporales, sin guardar contenido en memoria.
    """
    for register in temporaryRegisters + floatTemporaryRegisters:
      
      for object in tuple(self.registerDescriptor.getValuesInRegister(register)):
        
        # Actualizar descriptores
        self.registerDescriptor.removeValueFromRegister(register=register, value=object)
        self.addressDescriptor.replaceAddress(object, address=object)
          
  def saveTypeInHeapMemory(self, typeId, heapAddress):
    """
    Guarda el tipo en el primer byte de la dirección de memoria (en el heap).
    
    Modifica el valor de compilerTemporary[0].
    """
    
    if typeId not in (intId, floatId, stringId):
      raise Exception("Tipo no soportado.", typeId)
    
    self.addAssemblyCode(f"li {compilerTemporary[0]}, {typeId} # Guardar tipo en heap")
    self.addAssemblyCode(f"sb {compilerTemporary[0]}, 0({heapAddress})")
  
  def getTypeFromHeapMemory(self, object, register):
    """
    Obtiene el tipo de un objeto guardado en memoria dinámica.
    Lo guarda en el registro register.
    
    Modifica el registro dado en register.
    """
    self.addAssemblyCode(f"lw {register}, {self.getOffset(object)}({self.getBasePointer(object)})")
    self.addAssemblyCode(f"lb {register}, 0({register})")
    
    
  def translateInstruction(self, instruction):
    
    if isinstance(instruction, SingleInstruction):
      
      if instruction.operator == STORE:
        # Asignación
        self.translateValueStore(instruction)
        return
      
      elif instruction.operator == STORE_CONST:
        # Guardar variable como constante del compilador
        self.constants[instruction.arg2] = instruction.result
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
      
      # elif instruction.operator == ASSIGN:
      #   self.translateAssignmentInstruction(instruction)
      #   return
      
      elif instruction.operator in (ASSIGN, STRICT_ASSIGN):
        self.translateStrictAssignmentInstruction(instruction)
        return
      elif instruction.operator == NEG:
        self.translateNegativeOperation(instruction)
        return
      
      elif instruction.operator == PRINT_STR:
        self.translateStringPrint(instruction)
        return

      elif instruction.operator in (EQUAL, NOT_EQUAL, LESS, LESS_EQUAL, GREATER, GREATER_EQUAL):
        self.translateComparisonOperation(instruction)
        return

      elif instruction.operator == GOTO:
        self.translateJumpInstruction(instruction)
        return
      
      elif instruction.operator == LABEL:
        self.translateLabelInstruction(instruction)
        return
      
      elif instruction.operator == CONCAT:
        self.translateConcatInstruction(instruction)
        return
      
      elif instruction.operator == INT_TO_STR:
        self.translateIntToStrInstruction(instruction)
        return
      
      elif instruction.operator == FLOAT_TO_STR:
        self.translateFloatToStrInstruction(instruction)
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
      
      elif instruction.operator == FUNCTION:
        self.translateFunctionDeclaration(instruction)
        return
      
      elif instruction.operator == END_FUNCTION:
        self.translateFunctionDeclarationEnd(instruction)
        return
      
      elif instruction.operator == GET_ARG:
        self.translateGetArgInstruction(instruction)
        return
      
      elif instruction.operator == RETURN:
        self.translateReturnInstruction(instruction)
        return
      
      elif instruction.operator == CALL:
        self.translateCallInstruction(instruction)
        return
      
      elif instruction.operator == RETURN_VAL:
        self.translateReturnValueInstruction(instruction)
        return
      
      elif instruction.operator == PARAM:
        self.translateParamInstruction(instruction)
        return
      
      elif instruction.operator == PRINT_ANY:
        self.translateAnyPrint(instruction)
        return
      
      elif instruction.operator == MALLOC:
        self.translateMallocInstruction(instruction)
        return

    elif isinstance(instruction, ConditionalInstruction):
      self.translateConditionalJumpInstruction(instruction)
      return
    
    raise NotImplementedError("Instrucción no soportada.", str(instruction))
  
  def createHeapMemory(self, size, staticMemoryObject):
    """
    Reserva size cantidad de bytes en memoria dinámica y retorna (en texto) el registro que contiene la dirección.
    @param size: Tamaño en bytes de la memoria a reservar.
    @param staticMemoryObject: Objeto al que corresponde la memoria reservada. En su offset se guardará la dirección.
      Si es None, no se guardará la dirección en memoria estática.
    
    Modifica el valor de $a0 y $v0.
    """
    self.addAssemblyCode(f"li $v0, 9")
    self.addAssemblyCode(f"li $a0, {size}")
    self.addAssemblyCode("syscall")
    
    # Guardar en memoria estática la dirección del valor en el heap
    if staticMemoryObject != None:
      self.addAssemblyCode(f"sw $v0, {self.getOffset(staticMemoryObject)}({self.getBasePointer(staticMemoryObject)})")
    
    return "$v0"
    
  def translateValueStore(self, instruction):
    
    destination = instruction.result
    value = instruction.arg1.value if instruction.arg1.value != None else 0 # Considerar nil
    valueType = instruction.arg1.type
        
    if valueType.equalsType((IntType, BoolType, NilType)):
      # Asignación de número
      memoryAddressReg = self.createHeapMemory(numberSize + 4, destination)
      
      # Guardar el tipo en el heap
      self.saveTypeInHeapMemory(intId, memoryAddressReg)      
      
      # Guardar en registro el valor final
      register = self.getRegister(objectToSave=destination)
      self.addAssemblyCode(f"li {register}, {value}")

      # Guardar en descriptores que la variable está en el registro
      self.registerDescriptor.replaceValueInRegister(register, destination)
      self.addressDescriptor.insertAddress(destination, register)
    
    elif isinstance(valueType, FloatType):
      # Asignación de número
      memoryAddressReg = self.createHeapMemory(numberSize + 4, destination)
      
      # Guardar el tipo en el heap
      self.saveTypeInHeapMemory(floatId, memoryAddressReg) 
      
      # Mover dirección de memoria creada a registro seguro
      self.addAssemblyCode(f"move {compilerTemporary[1]}, {memoryAddressReg}")
      memoryAddressReg = compilerTemporary[1]
      
      # Guardar el valor en memoria (offset de 4 para omitir el byte de tipo)
      self.addAssemblyCode(f"li {compilerTemporary[0]}, {decimal_to_ieee754(value)} # Float store")
      self.addAssemblyCode(f"sw {compilerTemporary[0]}, 4({memoryAddressReg})")
      
      register = self.getRegister(objectToSave=destination, useFloat=True)
      self.addAssemblyCode(f"l.s {register}, 4({memoryAddressReg})") # 4 para omitir el byte de tipo
      
      # Guardar en descriptores que la variable está en el registro y en memoria
      self.registerDescriptor.replaceValueInRegister(register, destination)
      self.addressDescriptor.insertAddress(destination, register)
      self.addressDescriptor.insertAddress(destination, destination)
      
    elif valueType.strictEqualsType(StringType):      
      
      # Calcular tamaño: -2 por las comillas, + 1 por el caracter nulo, + 1 por el tipo
      size = len(value) - 2 + 1 + 1
      memoryAddressReg = self.createHeapMemory(size, destination)
      
      # Guardar el tipo en el heap
      self.saveTypeInHeapMemory(stringId, memoryAddressReg)
      
      # Mover dirección de memoria creada a registro seguro
      self.addAssemblyCode(f"move {compilerTemporary[1]}, {memoryAddressReg}")
      memoryAddressReg = compilerTemporary[1]
      
      # Agregar código assembly para guardar cada caracter en memoria
      # Comienza a escribir en 1 para omitir el byte detipo
      for i, char in enumerate(value[1:-1]):
        charPosition = i + 1
        self.addAssemblyCode(f"li {compilerTemporary[0]}, {ord(char)}   # Caracter {char}")
        self.addAssemblyCode(f"sb {compilerTemporary[0]}, {charPosition}({memoryAddressReg})")
        
      # Agregar caracter nulo al final
      self.addAssemblyCode(f"li {compilerTemporary[0]}, 0   # Caracter nulo")
      self.addAssemblyCode(f"sb {compilerTemporary[0]}, {size - 1}({memoryAddressReg})")
      
      # Guardar en registro la dirección de memoria del inicio del string
      register = self.getRegister(objectToSave=destination)
      self.addAssemblyCode(f"move {register}, {memoryAddressReg}  # Guardar dirección de memoria del string")
      
      # Actualizar descriptores
      self.registerDescriptor.saveValueInRegister(register, value=destination)
      self.addressDescriptor.insertAddress(object=destination, address=register)
      self.addressDescriptor.insertAddress(object=destination, address=destination)
      
      
      
  def translateIntPrint(self, instruction):
    
    value = instruction.arg1
    
    # Obtener ubicación más reciente    
    address = self.getValueInRegister(value, typeId=intId)
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
    address = self.getValueInRegister(value, typeId=floatId)
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
    address = self.getValueInRegister(value, typeId=stringId)
    
    # Cargar e imprimir cada caracter hasta encontrar el nulo
    loopLabel = f"print_string_{getUniqueId()}"
    endLabel = f"end_print_string_{getUniqueId()}"
    
    self.addAssemblyCode(f"move {compilerTemporary[0]}, {address} # Guardar dirección de memoria del string")
    self.addAssemblyCode(f"addi {compilerTemporary[0]}, {compilerTemporary[0]}, 1") # Ignorar byte de tipo
    
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
    
  
  def translateAnyPrint(self, instruction):
    
    # Se verifica el tipo guardado en el primer byte de la dirección de memoria
    # y se ejecuta una estructura de if else para determinar si operar como int, float o string
    
    value = instruction.arg1
    
    # Liberar registros (región ambigua)
    self.freeAllRegisters()
    
    # Obtener ubicación de inicio de bloque de mem en el heap
    self.addAssemblyCode(f"lw {compilerTemporary[0]}, {self.getOffset(value)}({self.getBasePointer(value)})")
    
    floatPrintLabel = f"print_float_{getUniqueId()}"
    stringPrintLabel = f"print_string_{getUniqueId()}"
    endPrintLabel = f"end_print_{getUniqueId()}"
    
    # Obtener tipo
    self.addAssemblyCode(f"lb {compilerTemporary[0]}, 0({compilerTemporary[0]})")
    
    # Estructura de if else
    self.addAssemblyCode(f"li {compilerTemporary[1]}, {stringId}")
    self.addAssemblyCode(f"beq {compilerTemporary[0]}, {compilerTemporary[1]}, {stringPrintLabel}")
    
    self.addAssemblyCode(f"li {compilerTemporary[1]}, {floatId}")
    self.addAssemblyCode(f"beq {compilerTemporary[0]}, {compilerTemporary[1]}, {floatPrintLabel}")
    
    # Por defecto es un int
    self.translateIntPrint(instruction)
    self.freeAllRegisters(saveValues=False)
    self.addAssemblyCode(f"j {endPrintLabel}")
    
    # Imprimir como float
    self.addAssemblyCode(f"{floatPrintLabel}:")
    self.translateFloatPrint(instruction)
    self.freeAllRegisters(saveValues=False)
    self.addAssemblyCode(f"j {endPrintLabel}")
    
    # Imprimir como string
    self.addAssemblyCode(f"{stringPrintLabel}:")
    self.translateStringPrint(instruction)
    self.freeAllRegisters(saveValues=False)
    
    self.addAssemblyCode(f"{endPrintLabel}:")
  
  def addArithmeticOperation(self, resultReg, value1Reg, value2Reg, operation, floatOperation):
    """
    Agrega el código para realizar una operación aritmética.
    
    Modifica: resultReg
    """
    operationMap = {
        PLUS: ("add", "add.s"),
        MINUS: ("sub", "sub.s"),
        MULTIPLY: ("mul", "mul.s"),
        DIVIDE: ("div", "div.s"),
        MOD: ("remu",)
      }
      
    # Realizar la operación
    if not floatOperation:
      self.addAssemblyCode(f"{operationMap[operation][0]} {resultReg}, {value1Reg}, {value2Reg}")
      
    elif operation != MOD:
      self.addAssemblyCode(f"{operationMap[operation][1]} {resultReg}, {value1Reg}, {value2Reg}")
      
    else: # MOD float 
      
      # División (float)
      self.addAssemblyCode(f"div.s {resultReg}, {value1Reg}, {value2Reg}")
      # Convertir cociente a entero (truncamiento)
      self.addAssemblyCode(f"floor.w.s {resultReg}, {resultReg}")
      # Convertir a float de nuevo
      self.addAssemblyCode(f"cvt.s.w {resultReg}, {resultReg}")
      # mult parte entera * divisor
      self.addAssemblyCode(f"mul.s {resultReg}, {resultReg}, {value2Reg}")
      # calcular modulo (dividendo - parte entera * divisor)
      self.addAssemblyCode(f"sub.s {resultReg}, {value1Reg}, {resultReg}")
      
      
  def translateArithmeticOperationWithType(self, instruction):
      
      values = (instruction.arg1, instruction.arg2)
      destination = instruction.result
      operation = instruction.operator
      
      # Obtener ubicación más reciente
      
      floatOperation = operation == DIVIDE or values[0].strictEqualsType(FloatType) or values[1].strictEqualsType(FloatType)
      
      # Reservar ubicación en heap correspondiente al resultado
      heapAddress = self.createHeapMemory(numberSize + 4, destination)
      
      # Guardar el tipo
      typeId = floatId if floatOperation else intId
      self.saveTypeInHeapMemory(typeId, heapAddress)
      
      
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
      
      # Realizar la operación
      if not floatOperation:
        resultReg = self.getRegister(objectToSave=destination, ignoreRegisters=addresses)
        self.addArithmeticOperation(resultReg, addresses[0], addresses[1], operation, floatOperation)
        
      elif operation != MOD:
        resultReg = self.getRegister(objectToSave=destination, useFloat=True, ignoreRegisters=addresses)
        self.addArithmeticOperation(resultReg, addresses[0], addresses[1], operation, floatOperation)
        
      else: # MOD float 
        
        resultReg = self.getRegister(objectToSave=destination, useFloat=True, ignoreRegisters=addresses)
        self.addArithmeticOperation(resultReg, addresses[0], addresses[1], operation, floatOperation)
        
      # Actualizar descriptores
      self.registerDescriptor.replaceValueInRegister(resultReg, destination)
      self.addressDescriptor.replaceAddress(destination, resultReg)
  
  def translateAnyArithmeticOperation(self, instruction):
    """
    Se utiliza cuando alguno de los dos operandos es any (o ambos).
    """
    
    values = (instruction.arg1, instruction.arg2)
    destination = instruction.result
    operator = instruction.operator
    
    # Guardar en memoria si está en registro
    for value in values:
      address = self.addressDescriptor.getAddress(value)
      
      if isinstance(address, Register):
        self.saveRegisterValueInMemory(register=address, object=value)
    
    # Reservar registros temporales
    tempReg = self.getRegister(objectToSave=None)
    floatTempReg = self.getRegister(objectToSave=None, useFloat=True)
    
    # Reservar ubicación en heap correspondiente al resultado
    heapAddress = self.createHeapMemory(numberSize + 4, destination)
    
    # Obtener tipos
    self.getTypeFromHeapMemory(object=values[0],register=compilerTemporary[0])
    self.getTypeFromHeapMemory(object=values[1],register=compilerTemporary[1])
    
    arithFloatLabel = f"arith_float_{getUniqueId()}"
    arithEndLabel = f"arith_end_{getUniqueId()}"
    
    self.addAssemblyCode("nop # Inicio de operación aritmética any")
    
    # Verificar si alguno de los valores es float
    self.addAssemblyCode(f"li {tempReg}, {floatId}")
    self.addAssemblyCode(f"beq {compilerTemporary[0]}, {tempReg}, {arithFloatLabel}")
    self.addAssemblyCode(f"beq {compilerTemporary[1]}, {tempReg}, {arithFloatLabel}")
    
    # Ambos son enteros
    
    # cargar valores
    for i in range(2):
      self.addAssemblyCode(f"lw {compilerTemporary[i]}, {self.getOffset(values[i])}({self.getBasePointer(values[i])})")
      self.addAssemblyCode(f"lw {compilerTemporary[i]}, 4({compilerTemporary[i]})")
      
    # Realizar la operación
    self.addArithmeticOperation(tempReg, compilerTemporary[0], compilerTemporary[1], operator, floatOperation=False)
    
    # Guardar resultado en memoria
    self.addAssemblyCode(f"sw {tempReg}, 4({heapAddress})")
    
    # Guardar tipo int en resultado
    self.saveTypeInHeapMemory(intId, heapAddress)
    
    self.addAssemblyCode(f"j {arithEndLabel}")  
    
    
    # Alguno es float
    
    
    self.addAssemblyCode(f"{arithFloatLabel}:")
    
    # Verificar si cada uno es float, si no convertir
    for i in range(2):
      onlyLoadFloatLabel = f"only_load_float_{i}_{getUniqueId()}"
      endLoadFloatLabel = f"end_load_float_{i}_{getUniqueId()}"
      
      self.addAssemblyCode(f"beq {compilerTemporary[i]}, {tempReg}, {onlyLoadFloatLabel}")
      
      # Convertir a float
      # Cargar valor en registro int. CompilerTemporary[i] = valor int
      self.addAssemblyCode(f"lw {compilerTemporary[i]}, {self.getOffset(values[i])}({self.getBasePointer(values[i])})")
      self.addAssemblyCode(f"lw {compilerTemporary[i]}, 4({compilerTemporary[i]})")
      
      self.addAssemblyCode(f"mtc1 {compilerTemporary[i]}, {floatCompilerTemporary[i]}") # Mover a registro float
      self.addAssemblyCode(f"cvt.s.w {floatCompilerTemporary[i]}, {floatCompilerTemporary[i]}") # Convertir a float
      
      self.addAssemblyCode(f"j {endLoadFloatLabel}")
      
      # Solo cargar valor float
      self.addAssemblyCode(f"{onlyLoadFloatLabel}:")
      self.addAssemblyCode(f"lw {compilerTemporary[i]}, {self.getOffset(values[i])}({self.getBasePointer(values[i])})")
      self.addAssemblyCode(f"l.s {floatCompilerTemporary[i]}, 4({compilerTemporary[i]})")
      
      self.addAssemblyCode(f"{endLoadFloatLabel}:")
    
    
    # Ya se tienen los valores en registros flotantes, realizar la operación
    self.addArithmeticOperation(floatTempReg, floatCompilerTemporary[0], floatCompilerTemporary[1], operator, floatOperation=True)
    
    # Guardar resultado en memoria
    self.addAssemblyCode(f"s.s {floatTempReg}, 4({heapAddress})")
    
    # Guardar tipo float en resultado
    self.saveTypeInHeapMemory(floatId, heapAddress)
    
    
    self.addAssemblyCode(f"{arithEndLabel}:") # Etiqueta para que int salte a este punto
    
  
  def translateArithmeticOperation(self, instruction):
    
    value1 = instruction.arg1
    value2 = instruction.arg2
    
    isValue1Any = not (value1.strictEqualsType((IntType, NilType, BoolType)) or value1.strictEqualsType(FloatType))
    isValue2Any = not (value2.strictEqualsType((IntType, NilType, BoolType)) or value2.strictEqualsType(FloatType))
    
    if not isValue1Any and not isValue2Any:
      # Ambos son de tipo conocido
      self.translateArithmeticOperationWithType(instruction)
      
    else:
      # Al menos uno es any
      self.translateAnyArithmeticOperation(instruction)
      
      
      
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
    
    
    
    isValueAny = not (value.strictEqualsType((IntType, NilType, BoolType)) or value.strictEqualsType(FloatType) or value.strictEqualsType(StringType))
    isResultAny = not (result.strictEqualsType((IntType, NilType, BoolType)) or result.strictEqualsType(FloatType) or result.strictEqualsType(StringType))
    
    if value.strictEqualsType(StringType):
      # Si es string, solo se debe mover la dirección de memoria
      valueReg = self.getValueInRegister(value)
      self.saveRegisterValueInMemory(register=valueReg, object=result, typeId=stringId)
    
    elif not isValueAny and not isResultAny:
      # Ambos son de tipo conocido
      
      # Si result es de tipo string, reservar nuevo espacio en memoria
      if result.strictEqualsType(StringType):
        heapMemory = self.createHeapMemory(numberSize + 4, result)
        self.saveTypeInHeapMemory(intId, heapMemory)
        
      valueReg = self.getValueInRegister(value)
      self.saveRegisterValueInMemory(register=valueReg, object=result)
    
    elif isValueAny or isResultAny:
      # Se debe realizar una verificación del tipo en tiempo de ejecución
      
      self.addAssemblyCode(f"nop # Asignación de tipo any")
      
      # Obtener el tipo de value
      self.addAssemblyCode(f"lw {compilerTemporary[0]}, {self.getOffset(value)}({self.getBasePointer(value)})")
      self.addAssemblyCode(f"lb {compilerTemporary[0]}, 0({compilerTemporary[0]})")
      
      endAssignmentLabel = f"end_strict_assignment_{getUniqueId()}"
      assignStringLabel = f"assign_string_{getUniqueId()}"
      assignNumberLabel = f"assign_number_{getUniqueId()}"
      saveNumberLabel = f"save_number_{getUniqueId()}"
      
      # Verificar si el tipo de value es strign. Si lo es solo asignar dirección de string a result.
      self.addAssemblyCode(f"li {compilerTemporary[1]}, {stringId}")
      self.addAssemblyCode(f"beq {compilerTemporary[0]}, {compilerTemporary[1]}, {assignStringLabel}")
      
      # Obtener dirección de heap de result
      self.addAssemblyCode(f"lw {compilerTemporary[1]}, {self.getOffset(result)}({self.getBasePointer(result)})")
      
      # Si la dirección no existe, crear como number
      self.addAssemblyCode(f"beqz {compilerTemporary[1]}, {assignNumberLabel}")
      
      # Si la dirección existe y es de tipo string, crear y reemplazar con memoria number
      self.addAssemblyCode(f"lb {compilerTemporary[1]}, 0({compilerTemporary[1]})") # Obtener tipo de result
      self.addAssemblyCode(f"li $a0, {stringId}")
      self.addAssemblyCode(f"beq {compilerTemporary[1]}, $a0, {assignNumberLabel}")
      
      # Else, la dirección en el heap ya es adecuada, guardar el número
      self.addAssemblyCode(f"j {saveNumberLabel}")  
      
      # Asignar string
      self.addAssemblyCode(f"{assignStringLabel}:")
      self.addAssemblyCode(f"lw {compilerTemporary[0]}, {self.getOffset(value)}({self.getBasePointer(value)})")
      self.addAssemblyCode(f"sw {compilerTemporary[0]}, {self.getOffset(result)}({self.getBasePointer(result)})")
      self.addAssemblyCode(f"j {endAssignmentLabel}")
      
      # Asignar number
      self.addAssemblyCode(f"{assignNumberLabel}:")
      heapMemory = self.createHeapMemory(numberSize + 4, result)
      self.addAssemblyCode(f"sb {compilerTemporary[0]}, 0({heapMemory})") # Guardar tipo en memoria creada
      
      
      # Guardar valor de number en memoria
      self.addAssemblyCode(f"{saveNumberLabel}:")
      valueReg = self.getValueInRegister(value, typeId=intId, updateDescriptors=False)
      self.saveRegisterValueInMemory(register=valueReg, object=result)
      
      
      self.addAssemblyCode(f"{endAssignmentLabel}:")
    
    # Si variable result no es any, actualizar descriptores
    if not isResultAny:
    # Eliminar valor de registro en descriptores
      resultPrevAddr = self.addressDescriptor.getAddress(result)
      if isinstance(resultPrevAddr, Register):
        # Si era un registro, eliminar el valor anterior de este
        self.registerDescriptor.removeValueFromRegister(register=resultPrevAddr, value=result)
        
      self.addressDescriptor.replaceAddress(object=result, address=result) # Eliminar registros de address de result
    
  def negativeOperationWithType(self, instruction):
    
    value = instruction.arg1
    destination = instruction.result
    
    # Obtener ubicación más reciente
    address = self.getValueInRegister(value)
    
    floatOperation = value.strictEqualsType(FloatType)
    
    # Reservar ubicación en heap correspondiente al resultado
    heapAddress = self.createHeapMemory(numberSize + 4, destination)
    
    # Guardar el tipo
    typeId = floatId if floatOperation else intId
    self.saveTypeInHeapMemory(typeId, heapAddress)
    
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
  
  
  def anyNegativeOperation(self, instruction):
    
    value = instruction.arg1
    destination = instruction.result
    
    # Reservar espacio para resultado
    heapAddress = self.createHeapMemory(numberSize + 4, destination)
    
    # Obtener tipo del valor
    self.getTypeFromHeapMemory(value, compilerTemporary[1])
    
    # Guardar tipo resultante en heap
    self.addAssemblyCode(f"sb {compilerTemporary[1]}, 0({heapAddress})")
    
    floatNegationLabel = f"float_negation_{getUniqueId()}"
    endNegationLabel = f"end_negation_{getUniqueId()}"
    
    # Verificar tipo
    self.addAssemblyCode(f"li {compilerTemporary[0]}, {floatId}")
    self.addAssemblyCode(f"beq {compilerTemporary[0]}, {compilerTemporary[1]}, {floatNegationLabel}")
    
    # Es un entero
    
    # Cargar valor del número entero y negarlo
    self.addAssemblyCode(f"lw {compilerTemporary[0]}, {self.getOffset(value)}({self.getBasePointer(value)})")
    self.addAssemblyCode(f"lw {compilerTemporary[0]}, 4({compilerTemporary[0]})")
    self.addAssemblyCode(f"neg {compilerTemporary[0]}, {compilerTemporary[0]}")
    
    # Guardar en memoria
    self.addAssemblyCode(f"sw {compilerTemporary[0]}, 4({heapAddress})")
    self.addAssemblyCode(f"j {endNegationLabel}")
    
    
    # Es un float
    
    self.addAssemblyCode(f"{floatNegationLabel}:")
    
    # Cargar valor del número float y negarlo
    self.addAssemblyCode(f"lw {compilerTemporary[0]}, {self.getOffset(value)}({self.getBasePointer(value)})")
    self.addAssemblyCode(f"l.s {floatCompilerTemporary[0]}, 4({compilerTemporary[0]})")
    self.addAssemblyCode(f"neg.s {floatCompilerTemporary[0]}, {floatCompilerTemporary[0]}")
    
    # Guardar en memoria
    self.addAssemblyCode(f"s.s {floatCompilerTemporary[0]}, 4({heapAddress})")
    
    
    self.addAssemblyCode(f"{endNegationLabel}:")
  
  
  def translateNegativeOperation(self, instruction):
    value = instruction.arg1
    
    isAny = not (value.strictEqualsType((IntType, NilType, BoolType)) or value.strictEqualsType(FloatType))
    
    if isAny:
      self.anyNegativeOperation(instruction)
    else:
      self.negativeOperationWithType(instruction)
    
  def simpleComparisonOperation(self, resultReg, value1Reg, value2Reg, operation, floatOperation):
    
    # Cargar valores en registros
    addresses = [value1Reg, value2Reg]
    
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
      self.addAssemblyCode(f"{operationMap[operation][0]} {resultReg}, {addresses[0]}, {addresses[1]} # Comparación entera")
      
    else:
      # Operación float
      # Mayor, mayor o igual y no igual se invierten
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
      
  
  def simpleComparisonOperationWithType(self, resultReg, value1, value2, value1Reg, value2Reg, operation, floatOperation):
    
    values = (value1, value2)
    addresses = [value1Reg, value2Reg]
    
    # Realizar conversión de tipos si es necesario
    if floatOperation:
      
      for i in range(2):
        if not values[i].strictEqualsType(FloatType):
          
          self.addAssemblyCode(f"mtc1 {addresses[i]} {floatCompilerTemporary[i]}")
          self.addAssemblyCode(f"cvt.s.w {floatCompilerTemporary[i]}, {floatCompilerTemporary[i]}")
          addresses[i] = floatCompilerTemporary[i]
    
    self.simpleComparisonOperation(resultReg, addresses[0], addresses[1], operation, floatOperation)
      
  
  def stringComparisonOperation(self, resultReg, value1Reg, value2Reg, operation):
    """
    Se encarga de comparar dos strings.
    @param resultReg: Registro donde se guardará el resultado.
    @param value1Reg: Registro donde se encuentra la dirección de mem de inicio del primer string.
    @param value2Reg: Registro donde se encuentra la dirección de mem de inicio del segundo string.
    @param operation: Operación de comparación a realizar.
    
    Modifica: resultReg
    Value1Reg y value2Reg no pueden ser compilerTemporary.
    """
    
    # Cargar valores en registros
    addresses = [value1Reg, value2Reg]
    
    for addr in addresses:
      if addr in compilerTemporary:
        raise ValueError("Los registros temporales del compilador no pueden ser utilizados para comparación de strings.")
      
    repeatLabel = f"repeat_string_comp_{getUniqueId()}"
    equalLabel = f"equal_string_comp_{getUniqueId()}"
    endLabel = f"end_string_comp_{getUniqueId()}"
    charDiffLabel = f"char_diff_{getUniqueId()}"
    
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
  
  
  def anyComparisonOperation(self, resultReg, value1, value2, operation):
    
    values = (value1, value2)
    
    # Guardar en memoria si está en registro
    for value in values:
      address = self.addressDescriptor.getAddress(value)
      
      if isinstance(address, Register):
        self.saveRegisterValueInMemory(register=address, object=value)
    
    # Reservar registros temporales
    tempReg = self.getRegister(objectToSave=None)
    tempReg2 = self.getRegister(objectToSave=None, ignoreRegisters=[tempReg])
    
    
    self.addAssemblyCode(f"nop # Comparación de tipo any")
    
    # Obtener tipos
    self.getTypeFromHeapMemory(object=values[0],register=compilerTemporary[0])
    self.getTypeFromHeapMemory(object=values[1],register=compilerTemporary[1])
    
    
    floatCompLabel = f"float_comp_{getUniqueId()}"
    stringCompLabel = f"string_comp_{getUniqueId()}"
    endCompLabel = f"end_comp_{getUniqueId()}"
    
    # Verificar si alguno de los valores es float
    self.addAssemblyCode(f"li {tempReg}, {floatId}")
    self.addAssemblyCode(f"beq {compilerTemporary[0]}, {tempReg}, {floatCompLabel}")
    self.addAssemblyCode(f"beq {compilerTemporary[1]}, {tempReg}, {floatCompLabel}")
    
    # Verificar si alguno de los valores es string
    self.addAssemblyCode(f"li {tempReg}, {stringId}")
    self.addAssemblyCode(f"beq {compilerTemporary[0]}, {tempReg}, {stringCompLabel}")
    self.addAssemblyCode(f"beq {compilerTemporary[1]}, {tempReg}, {stringCompLabel}")
    
    
    # Comparación entera
    # Cargar ambos valores
    for i in range(2):
      self.addAssemblyCode(f"lw {compilerTemporary[i]}, {self.getOffset(values[i])}({self.getBasePointer(values[i])})")
      self.addAssemblyCode(f"lw {compilerTemporary[i]}, 4({compilerTemporary[i]})")
      
    # Realizar la operación
    self.simpleComparisonOperation(resultReg, compilerTemporary[0], compilerTemporary[1], operation, floatOperation=False)
    
    self.addAssemblyCode(f"j {endCompLabel}") # Saltar al final (skip string y float)

    
    # Comparación float
    
    self.addAssemblyCode(f"{floatCompLabel}:")
    
    # Verificar si cada uno es float, si no convertir
    # tempreg sigue siendo floatId
    for i in range(2):
      onlyLoadFloatLabel = f"only_load_float_{i}_{getUniqueId()}"
      endLoadFloatLabel = f"end_load_float_{i}_{getUniqueId()}"
      
      self.addAssemblyCode(f"beq {compilerTemporary[i]}, {tempReg}, {onlyLoadFloatLabel}")
      
      # Convertir a float
      # floatCompilerTemporary[i] = valor float
      self.addAssemblyCode(f"lw {compilerTemporary[i]}, {self.getOffset(values[i])}({self.getBasePointer(values[i])})")
      self.addAssemblyCode(f"l.s {floatCompilerTemporary[i]}, 4({compilerTemporary[i]})")
      self.addAssemblyCode(f"cvt.s.w {floatCompilerTemporary[i]}, {floatCompilerTemporary[i]}") # Convertir a float
      
      self.addAssemblyCode(f"j {endLoadFloatLabel}")
      
      # Solo cargar valor en registro float
      self.addAssemblyCode(f"{onlyLoadFloatLabel}:")
      self.addAssemblyCode(f"lw {compilerTemporary[i]}, {self.getOffset(values[i])}({self.getBasePointer(values[i])})")
      self.addAssemblyCode(f"l.s {floatCompilerTemporary[i]}, 4({compilerTemporary[i]})")
      
      self.addAssemblyCode(f"{endLoadFloatLabel}:")
      
    # Ya se tienen los valores en registros flotantes, realizar la operación
    self.simpleComparisonOperation(resultReg, floatCompilerTemporary[0], floatCompilerTemporary[1], operation, floatOperation=True)
    
    self.addAssemblyCode(f"j {endCompLabel}") # Saltar al final (SKIP STRING)
      
    
    # Comparación string
    
    self.addAssemblyCode(f"{stringCompLabel}:")
    
    # Cargar direcciones de memoria de strings
    stringRegs = [tempReg, tempReg2]
    for i in range(2):
      self.addAssemblyCode(f"lw {stringRegs[i]}, {self.getOffset(values[i])}({self.getBasePointer(values[i])})")
      
    self.stringComparisonOperation(resultReg, stringRegs[0], stringRegs[1], operation)
    
    
    self.addAssemblyCode(f"{endCompLabel}:")
    
    
    
  def translateComparisonOperation(self, instruction):
    
    values = (instruction.arg1, instruction.arg2)
    destination = instruction.result
    operation = instruction.operator
    
    anyOperation = any([not (value.strictEqualsType((IntType, NilType, BoolType)) or \
                        value.strictEqualsType(FloatType) or value.strictEqualsType(StringType))
                        for value in values])
    
    floatOperation = any([value.strictEqualsType(FloatType) for value in values])
    stringOperation = any([value.strictEqualsType(StringType) for value in values])
    
    # Reservar ubicación en heap correspondiente al resultado
    heapAddress = self.createHeapMemory(numberSize + 4, destination)
    
    # Guardar el tipo
    self.saveTypeInHeapMemory(intId, heapAddress) # Resultado bool: entero
      
    resultReg = self.getRegister(objectToSave=destination)
      
    if anyOperation:
      # Al menos uno es any
      self.anyComparisonOperation(resultReg, values[0], values[1], operation)
    else:
      # Todos los operadores son de tipo conocido
      
      # Cargar valores en registros
      addresses = [None, None]
      for i in range(2):
        addresses[i] = self.getValueInRegister(values[i], ignoreRegisters=addresses + [resultReg])
      
      if stringOperation:
        # Comparación de strings
        self.stringComparisonOperation(resultReg, addresses[0], addresses[1], operation)
        
      elif floatOperation:
        # Comparación de bools
        self.simpleComparisonOperationWithType(resultReg, values[0], values[1], addresses[0], addresses[1], operation, floatOperation)
      else:
        # Comparación entera
        self.simpleComparisonOperationWithType(resultReg, values[0], values[1], addresses[0], addresses[1], operation, floatOperation)
        
    # Actualizar descriptores. Salida siempre es bool
    self.registerDescriptor.replaceValueInRegister(resultReg, destination)
    self.addressDescriptor.replaceAddress(destination, resultReg)
    
  
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
    
    
  def concatOperation(self, stringResultReg, string1Reg, string2Reg, tempReg):
    """
    Añadir código para concatenar dos strings.
    @param stringResultReg: Registro donde se guardará la dirección de memoria del nuevo string.
    @param string1Reg: Registro donde se encuentra la dirección de memoria del primer string.
    @param string2Reg: Registro donde se encuentra la dirección de memoria del segundo string.
    @param tempReg: Registro temporal.
    
    Modifica: stringResultReg, tempReg, compilerTemporary[0], compilerTemporary[1], $a0, $v0
    """
    
    
    # Obtener inicio de bloques de memoria de strings
    stringsReg = (string1Reg, string2Reg)
      
    # Registro que va a irse desplazando a lo largo de la palabra
    wordCopyReg = tempReg
    
    # Contar tamaño de strings
    self.addAssemblyCode(f"nop # translateConcatOperation: concatenar dos strings {stringsReg[0]} y {stringsReg[1]}")
    self.addAssemblyCode(f"li {compilerTemporary[0]}, 0   # Contador de tamaño de ambos strings")
    for i in range(2):
      strLenLoopLabel = f"str_len_loop{i+1}_{getUniqueId()}"
      strLenEndLabel = f"str_len_end{i+1}_{getUniqueId()}"
      
      # Copiar inicio de string a temporal, para que el original no se modifique
      self.addAssemblyCode(f"move {wordCopyReg}, {stringsReg[i]}   # Copiar dirección de memoria del string {i+1}")
      
      # Ignorar byte de tipo
      self.addAssemblyCode(f"addi {wordCopyReg}, {wordCopyReg}, 1")
      
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
      
    # Sumar 2 por el byte de tipo al inicio y por el caracter nulo al final
    self.addAssemblyCode(f"addi {compilerTemporary[0]}, {compilerTemporary[0]}, 2")
      
    # Reservar memoria para el nuevo string
    self.addAssemblyCode(f"li $v0, 9")
    self.addAssemblyCode(f"move $a0, {compilerTemporary[0]}   # Reservar en heap tamanio total de ambos strings")
    self.addAssemblyCode("syscall")
    
    # Guardar en registro resultante, la dirección de memoria del nuevo string
    self.addAssemblyCode(f"move {stringResultReg}, $v0")
    
    # Guardar el tipo en el heap
    self.saveTypeInHeapMemory(stringId, stringResultReg)
    
    
    # Copiar inicio de strings a temporal, el cuál se irá desplazando
    self.addAssemblyCode(f"move {compilerTemporary[0]}, {stringResultReg} # Copiar en temp inicio de string resultante")
    
    # Saltar el byte de tipo en string resultante
    self.addAssemblyCode(f"addi {compilerTemporary[0]}, {compilerTemporary[0]}, 1")
      
    # Iniciar a copiar strings
    loopCopyLabels = (f"copy_string1_{getUniqueId()}", f"copy_string2_{getUniqueId()}")
    endCopyLabels = (f"end_copy_string1_{getUniqueId()}", f"end_copy_string2_{getUniqueId()}")
    
    for i in range(2):     
      self.addAssemblyCode(f"move {wordCopyReg}, {stringsReg[i]}   # Copiar dirección de memoria del string {i+1}")
      self.addAssemblyCode(f"addi {wordCopyReg}, {wordCopyReg}, 1  # Ignorar byte de tipo")
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
    
    
  def translateConcatInstructionWithType(self, instruction):
    
    values = (instruction.arg1, instruction.arg2)
    destination = instruction.result
    
    # Obtener inicio de bloques de memoria de strings
    stringRegs = [None, None]
    for i in range(2):
      stringRegs[i] = self.getValueInRegister(values[i], ignoreRegisters=stringRegs)
      
    # Registro que va a irse desplazando a lo largo de la palabra
    wordCopyReg = self.getRegister(objectToSave=None, ignoreRegisters=stringRegs)
    
    # Obtener registro para guardar la dirección de memoria del nuevo string
    resultAddress = self.getRegister(objectToSave=destination, ignoreRegisters=[wordCopyReg]+ stringRegs)
    
    # Actualizar descriptores, indicar que el inicio del string resultante está en el registro
    self.addressDescriptor.replaceAddress(destination, resultAddress)
    self.registerDescriptor.saveValueInRegister(register=resultAddress, value=destination)
    
    self.concatOperation(resultAddress, stringRegs[0], stringRegs[1], wordCopyReg)
    
    # Guardar en memoria estática string resultante
    self.addAssemblyCode(f"sw {resultAddress}, {self.getOffset(destination)}({self.getBasePointer(destination)})")
  
  def translateAnyConcatInstruction(self, instruction):
    """
    Agrega el código para concatenar dos strings en donde hay valores any.
    Siempre uno de los dos operadores debe ser string
    """
    
    values = (instruction.arg1, instruction.arg2)
    destination = instruction.result
    
    # Obtener operador string
    stringValue = None
    for value in values:
      if value.strictEqualsType(StringType):
        stringValue = value
        break
      
    # Obtener operador any
    anyValue = values[0] if values[0] != stringValue else values[1]
    
    # Registro para guardar el string resultante de conversión a string
    anyValueAsStringReg = self.getRegister(objectToSave=None) 
    
    # Reservar registros temporales
    intTempRegs = []
    for _ in range(4):
      intTempRegs.append(self.getRegister(objectToSave=None, ignoreRegisters=[anyValueAsStringReg] + intTempRegs))

    
    intConcatConvLabel = f"int_concat_conversion_{getUniqueId()}"
    floatConcatConvLabel = f"float_concat_conversion_{getUniqueId()}"
    endConcatConvLabel = f"end_concat_conversion_{getUniqueId()}"
    
    # Verificar si el valor any es float
    self.addAssemblyCode(f"li {compilerTemporary[0]}, {floatId}")
    self.addAssemblyCode(f"lw {compilerTemporary[1]}, {self.getOffset(anyValue)}({self.getBasePointer(anyValue)})")
    self.addAssemblyCode(f"lb {compilerTemporary[1]}, 0({compilerTemporary[1]})")
    self.addAssemblyCode(f"beq {compilerTemporary[0]}, {compilerTemporary[1]}, {floatConcatConvLabel}")
    
    # Verificar si es int
    self.addAssemblyCode(f"li {compilerTemporary[0]}, {intId}")
    self.addAssemblyCode(f"beq {compilerTemporary[0]}, {compilerTemporary[1]}, {intConcatConvLabel}")    
    
    # Si no es number, es string
    # Cargar el valor de string en registro
    stringValueReg = self.getValueInRegister(anyValue, typeId=stringId, updateDescriptors=False)
    self.addAssemblyCode(f"move {anyValueAsStringReg}, {stringValueReg}")
    
    self.addAssemblyCode(f"j {endConcatConvLabel}")    
    
    # Es int, convertir int a string
    self.addAssemblyCode(f"{intConcatConvLabel}:")
    
    intNumberReg = self.getValueInRegister(anyValue,
                                            typeId=intId,
                                            updateDescriptors=False,
                                            ignoreRegisters=[anyValueAsStringReg] + intTempRegs)
    
    self.intToStrOperation(stringResultReg=anyValueAsStringReg,
                            tempNumberReg=intNumberReg, 
                            tempStringReg=intTempRegs[0],
                            tempStringReg2=intTempRegs[1],
                            destination=None)
    
    self.addAssemblyCode(f"j {endConcatConvLabel}")
    
    
    # Si es float, convertir float a string
    self.addAssemblyCode(f"{floatConcatConvLabel}:")
    
    floatNumberReg = self.getValueInRegister(anyValue,
                                              updateDescriptors=False,
                                              typeId=floatId,
                                              ignoreRegisters=[anyValueAsStringReg] + intTempRegs)
    
    floatAsString = self.floatToStrOperation(resultStringReg=anyValueAsStringReg,
                                              floatNumberReg=floatNumberReg,
                                              intTempReg=intTempRegs[0],
                                              decimalTempReg=intTempRegs[1],
                                              tempStringResultReg=intTempRegs[2],
                                              tempStringReg=intTempRegs[3])
    
    # Mover resultado de string a registro
    self.addAssemblyCode(f"move {anyValueAsStringReg}, {floatAsString}")
    
    self.addAssemblyCode(f"{endConcatConvLabel}:")
    
    # En este punto, anyValueAsStringReg contiene valor de number convertido a string
    # Cargar dirección de memoria de otro string y resultado
    
    stringValueReg = self.getValueInRegister(stringValue, ignoreRegisters=[anyValueAsStringReg, intTempRegs[0]])
    resultStringReg = self.getRegister(objectToSave=destination,
                                        ignoreRegisters=[anyValueAsStringReg, stringValueReg, intTempRegs[0]])
    
    # Si el orden se cambió al preferir string, voltear
    if stringValue == values[1]:
      stringValueReg, anyValueAsStringReg = anyValueAsStringReg, stringValueReg
    
    self.concatOperation(resultStringReg, stringValueReg, anyValueAsStringReg, intTempRegs[0])
    
    # Guardar en memoria estática string resultante
    self.addAssemblyCode(f"sw {resultStringReg}, {self.getOffset(destination)}({self.getBasePointer(destination)}) #LOL")
    
    # Actualizar descriptores
    self.registerDescriptor.replaceValueInRegister(resultStringReg, destination)
    self.addressDescriptor.replaceAddress(destination, resultStringReg)
    
  
  def translateConcatInstruction(self, instruction):
    
    values = (instruction.arg1, instruction.arg2)
    
    anyOperation = any([not value.strictEqualsType(StringType) for value in values])
    
    if anyOperation:
      # Al menos uno es any
      self.translateAnyConcatInstruction(instruction)
    else:
      # Todos son string
      self.translateConcatInstructionWithType(instruction)
  
  def intToStrOperation(self, stringResultReg, tempNumberReg, tempStringReg, tempStringReg2, destination=None):
    """
    Agrega el código para convertir un número int a str y guardarlo en el heap.
    @param stringResultReg: Registro donde se guardará la dirección de memoria de inicio del string.
    @param tempNumberReg: Registro temporal entero para operaciones.
    @param tempStringReg: Registro temporal para operaciones.
    @param tempStringReg2: Registro temporal para operaciones.
    @param destination: Objeto que representa la variable donde se guardará el resultado. Si es None, no se guarda en memoria estática el string.
    
    Modifica: stringResultReg, tempNumberReg, tempStringReg, tempStringReg2, compilerTemporary[0], compilerTemporary[1], 
        $a0 y $v0.
    """
    
    # Verificar si los parametros son repetidos
    params = set([str(reg) for reg in (stringResultReg, tempNumberReg, tempStringReg, tempStringReg2)])
    if len(params) < 4:
      raise ValueError(f"Los registros temporales no pueden ser repetidos en int to str operation: stringResultReg={stringResultReg}, tempNumberReg={tempNumberReg}, tempStringReg={tempStringReg}, tempStringReg2={tempStringReg2}")
  
    # Reservar espacio en heap para string
    memoryAddressReg = self.createHeapMemory(intAsStrSize + 1, destination)
    
    # Guardar el tipo en el heap
    self.saveTypeInHeapMemory(stringId, memoryAddressReg)
    
    # Guardar en registro la dirección de memoria del inicio del string
    self.addAssemblyCode(f"move {stringResultReg}, {memoryAddressReg}")
    
    # Guardar el divisor base 10

    handleZeroLabel = f"handle_zero_{getUniqueId()}"
    convertLoopLabel = f"convert_loop_{getUniqueId()}"
    endConvertLabel = f"end_convert_{getUniqueId()}"
    
    # Copiar inicio de string a registro temporal
    self.addAssemblyCode(f"move {tempStringReg}, {stringResultReg}")
    
    # Empezar en segundo byte (primer byte es para tipo)
    self.addAssemblyCode(f"addi {tempStringReg}, {tempStringReg}, 1")
    
    # Si el número es cero, convertirlo a '0' directamente
    self.addAssemblyCode(f"beqz {tempNumberReg}, {handleZeroLabel} # Si el número es cero, convertirlo a '0'")
    
    # Guardar divisor base 10
    self.addAssemblyCode(f"li {compilerTemporary[0]}, 10")
    
    self.addAssemblyCode(f"{convertLoopLabel}:")
    
    # Obtener digito menos significativo. 
    digitReg = compilerTemporary[1]
    self.addAssemblyCode(f"div {tempNumberReg}, {compilerTemporary[0]}  # Dividir por 10")
    self.addAssemblyCode(f"mfhi {digitReg}  # Obtener residuo (dig individual)")
    self.addAssemblyCode(f"mflo {tempNumberReg}  # Obtener cociente (num reducido)")
    
    # Si el número es cero, no agregar char y terminar
    
    # Convertir digito a caracter
    self.addAssemblyCode(f"addi {digitReg}, {digitReg}, 48  # Convertir a caracter ASCII")
    self.addAssemblyCode(f"sb {digitReg}, 0({tempStringReg})  # Guardar caracter en string")
    self.addAssemblyCode(f"addi {tempStringReg}, {tempStringReg}, 1  # Avanzar a siguiente caracter en buffer")
    
    self.addAssemblyCode(f"bne {tempNumberReg}, $zero, {convertLoopLabel} # Si no es cero, repetir")
    
    self.addAssemblyCode(f"sb $zero, 0({tempStringReg})  # Agregar caracter nulo al final")
    
    # Reverse loop
    
    # StringBufferReg está al final del string + 1 (caracter nulo)
    self.addAssemblyCode(f"subi {tempStringReg}, {tempStringReg}, 1  # Retroceder a último caracter")
    stringPointerBackwardReg = tempStringReg # Se va a ir decrementando
    
    # Guardar otra copia del string, para recorrer de adelante hacia atras
    stringPointerForwardReg = tempStringReg2 # Se va a ir incrementando
    self.addAssemblyCode(f"move {stringPointerForwardReg}, {stringResultReg}")
    
    # Sumar 1 para que apunte al primer caracter (ignorar tipo)
    self.addAssemblyCode(f"addi {stringPointerForwardReg}, {stringPointerForwardReg}, 1")
    
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
    self.addAssemblyCode(f"sb {compilerTemporary[0]}, 0({tempStringReg})  # Guardar '0' en string")
    
    # Agregar nulo luego de cero
    self.addAssemblyCode(f"addi {tempStringReg}, {tempStringReg}, 1  # Avanzar a siguiente caracter en buffer")
    self.addAssemblyCode(f"sb $zero, 0({tempStringReg})  # Agregar caracter nulo al final")
    
    
    self.addAssemblyCode(f"{endConvertLabel}:")
    
  
  def translateIntToStrInstruction(self, instruction):
    
    number = instruction.arg1
    destination = instruction.result
    
    # Obtener registro para guardar resultado
    stringResultReg = self.getRegister(objectToSave=destination)
    
    self.addressDescriptor.replaceAddress(destination, stringResultReg)
    self.registerDescriptor.saveValueInRegister(stringResultReg, value=destination)
    
    # Obtener ubicación más reciente del número.
    # No se actualizan descriptores porque se va a operar el número
    tempNumberReg = self.getValueInRegister(number, ignoreRegisters=[stringResultReg], updateDescriptors=False)

    # temporal para string
    tempStringReg = self.getRegister(objectToSave=None, ignoreRegisters=[stringResultReg, tempNumberReg])
    
    # Temporal 2 para string
    tempStringReg2 = self.getRegister(objectToSave=None, ignoreRegisters=[stringResultReg, tempStringReg, tempNumberReg])
    
    self.intToStrOperation(stringResultReg, tempNumberReg, tempStringReg, tempStringReg2, destination)
    
    
  def floatToIntOperation(self, intResultReg, floatReg):
    """
    Añade código para convertir float a int.
    @param intResultReg: Registro donde se guardará el resultado.
    @param floatReg: Registro donde se encuentra el valor float.
    
    Modifica: intResultReg, floatCompilerTemporary[0]
    """
        
    # Convertir float a int
    self.addAssemblyCode(f"cvt.w.s {floatCompilerTemporary[0]}, {floatReg}  # Convertir float a int")
    self.addAssemblyCode(f"mfc1 {intResultReg}, {floatCompilerTemporary[0]} # Mover int de registro f a int")
  
  def floatToStrOperation(self, resultStringReg, floatNumberReg, intTempReg, decimalTempReg, tempStringResultReg, tempStringReg):
    """
    Añadir código para convertir un float a string.
    
    @param resultStringReg: Registro donde se guardará la dirección de memoria del string resultante.
    @param floatNumberReg: Registro donde se encuentra el número float. Este no se modifica.
    @param intTempReg: Registro temporal ENTERO.
    @param decimalTempReg: Registro temporal ENTERO.
    @param tempStringResultReg: Registro temporal ENTERO.
    @param tempStringReg: Registro temporal ENTERO.
    
    @returns: Registro donde se guardará la dirección de memoria del string.
    
    Modifica:resultStringReg, floatCompilerTemporary[0], compilerTemporary[0], compilerTemporary[1], $a0 y $v0, resultStringReg, floatTempReg, intTempReg, decimalTempReg, tempStringResultReg, tempStringReg, tempStringReg2
    """
    
    # Verificar que los registros de parametros no se repitan
    params = set([str(reg) for reg in (resultStringReg, floatNumberReg, intTempReg, decimalTempReg, tempStringResultReg, tempStringReg)])
    if len(params) < 6:
      raise Exception(f"Los registros temporales no pueden ser repetidos en float to str operation: resultStringReg={resultStringReg}, floatNumberReg={floatNumberReg}, intTempReg={intTempReg}, decimalTempReg={decimalTempReg}, tempStringResultReg={tempStringResultReg}, tempStringReg={tempStringReg}")
    
    # Obtener parte entera
    self.addAssemblyCode(f"trunc.w.s {floatCompilerTemporary[0]}, {floatNumberReg}  # Obtener parte entera")
    self.addAssemblyCode(f"mfc1 {intTempReg}, {floatCompilerTemporary[0]}")
    
    # Obtener parte decimal
    self.addAssemblyCode(f"cvt.s.w {floatCompilerTemporary[0]}, {floatCompilerTemporary[0]}  # Convertir entero truncado a float")
    self.addAssemblyCode(f"sub.s {floatCompilerTemporary[0]}, {floatNumberReg}, {floatCompilerTemporary[0]}  # Obtener parte decimal")
    
    # Cargar factor de conversión de decimal a entero
    self.addAssemblyCode(f"li {compilerTemporary[0]}, 100000000  #Cargar factor de conversion de decimal a entero")
    self.addAssemblyCode(f"mtc1 {compilerTemporary[0]}, {floatCompilerTemporary[1]}")
    self.addAssemblyCode(f"cvt.s.w {floatCompilerTemporary[1]}, {floatCompilerTemporary[1]}")
    
    # Convertir parte decimal a entero
    self.addAssemblyCode(f"mul.s {floatCompilerTemporary[0]}, {floatCompilerTemporary[0]}, {floatCompilerTemporary[1]}  # Multiplicar decimal por factor")
    self.addAssemblyCode(f"trunc.w.s {floatCompilerTemporary[0]}, {floatCompilerTemporary[0]}  # Obtener parte decimal como entero")
    self.addAssemblyCode(f"mfc1 {decimalTempReg}, {floatCompilerTemporary[0]}")
    
    # Convertir parte entera a string
    self.intToStrOperation(tempStringResultReg, intTempReg, resultStringReg, tempStringReg)
    self.addAssemblyCode(f"move {intTempReg}, {tempStringResultReg}")
    
    # Convertir parte decimal a string
    self.intToStrOperation(tempStringResultReg, decimalTempReg, resultStringReg, tempStringReg)
    self.addAssemblyCode(f"move {decimalTempReg}, {tempStringResultReg}")
    
    # Concatenar parte entera y punto decimal
    # Cargar punto decimal
    self.addAssemblyCode(f"nop # antes de cargar punto {self.constants[CONST_POINT_CHAR]}")
    pointCharReg = self.getValueInRegister(self.constants[CONST_POINT_CHAR], ignoreRegisters=[tempStringResultReg, intTempReg, decimalTempReg, resultStringReg], updateDescriptors=False)
    self.concatOperation(tempStringResultReg, intTempReg, pointCharReg, resultStringReg)
    
    # Concatenar parte decimal
    self.concatOperation(resultStringReg, tempStringResultReg, decimalTempReg, tempStringReg)
    
    return resultStringReg
  
  def translateFloatToStrInstruction(self, instruction):
    
    value = instruction.arg1
    destination = instruction.result
    
    # Obtener registros
    floatNumberReg = self.getValueInRegister(value)
    intTempReg = self.getRegister(objectToSave=None, ignoreRegisters=[floatNumberReg])
    decimalTempReg = self.getRegister(objectToSave=None, ignoreRegisters=[floatNumberReg, intTempReg])
    tempStringResultReg = self.getRegister(objectToSave=None, ignoreRegisters=[floatNumberReg, intTempReg, decimalTempReg])
    tempStringReg = self.getRegister(objectToSave=None, ignoreRegisters=[floatNumberReg, intTempReg, decimalTempReg, tempStringResultReg])
    tempStringReg2 = self.getRegister(objectToSave=None, ignoreRegisters=[floatNumberReg, intTempReg, decimalTempReg, tempStringResultReg, tempStringReg])
    
    resultStringReg = self.floatToStrOperation(floatNumberReg, intTempReg, decimalTempReg,
                                                tempStringResultReg, tempStringReg, tempStringReg2)
    
    # Actualizar descriptores
    self.registerDescriptor.replaceValueInRegister(register=resultStringReg, value=destination)
    self.addressDescriptor.replaceAddress(object=destination, address=resultStringReg)
    
    
  def translateNotOperation(self, instruction):
    
    value = instruction.arg1
    destination = instruction.result
    
    isAny = not value.strictEqualsType(BoolType)
    
    # Obtener valor a negar en registro
    valueReg = self.getValueInRegister(value, updateDescriptors=(not isAny), typeId=intId)
    
    # Obtener ubicación de destino
    destinationReg = self.getRegister(objectToSave=destination, ignoreRegisters=[valueReg])
    
    # Negar valor
    self.addAssemblyCode(f"xori {destinationReg}, {valueReg}, 1  # Negar valor")
    
    # Actualizar descriptores para que solo destination tenga el valor
    self.registerDescriptor.replaceValueInRegister(destinationReg, destination)
    self.addressDescriptor.replaceAddress(destination, destinationReg)
  
  def translateFunctionDeclaration(self, instruction):
    
    functionDef = instruction.arg1
    functionName = functionDef.getUniqueName()
    functionOffset = functionDef.getBodyOffset() # Retorna el offset final, que es el tamaño del frame
    functionLevel = functionDef.getFunctionLevel()
    
    # Limpiar descriptores de registros (funciones son ambiguas)
    # Este código no se ejecuta con cada llamada de la función, es exclusivo del análisis de la 
    # declaración de la función
    self.freeAllRegisters()
    
    self.activeFunctions.append(functionName) # Inicia el contexto de la función
        
    # Añadir salto para evitar que se ejecute el código de la función fuera de una llamada
    self.addAssemblyCode(f"j {skipFunctionPrefix}_{functionName}")
    
    # Añadir etiqueta de inicio de función
    self.addAssemblyCode(f"{functionName}:")
    
    # En este punto ya están guardados los parametros en el stack
    
    # Guardar dirección de retorno
    self.addAssemblyCode(f"subu $sp, $sp, 4 # Push de dirección de retorno")
    self.addAssemblyCode(f"sw $ra, 0($sp)  # Guardar dirección de retorno")
    
    # Guardar function level de la función
    self.addAssemblyCode(f"subu $sp, $sp, 4 # Push de function level")
    self.addAssemblyCode(f"li {compilerTemporary[0]}, {functionLevel}")
    self.addAssemblyCode(f"sw {compilerTemporary[0]}, 0($sp) # Guardar function level")
    
    # Guardar frame pointer anterior
    self.addAssemblyCode(f"subu $sp, $sp, 4 # Push de frame pointer anterior")
    self.addAssemblyCode(f"sw $fp, 0($sp)  # Guardar frame pointer anterior")
    
    # Reemplazar frame pointer anterior por el actual
    self.addAssemblyCode(f"move $fp, $sp")
    
    # Mover $sp al final del frame
    self.addAssemblyCode(f"subu $sp, $sp, {functionOffset} # Mover $sp al final del frame")
    
    
  def translateFunctionDeclarationEnd(self, instruction):
    
    functionDef = instruction.arg1
    functionName = functionDef.getUniqueName()
    numParams = functionDef.getRealParamsNumber()
    
    # Agregar etiqueta a la que apuntan los returns para ejecutar desmontaje de registro de activación
    self.addAssemblyCode(f"{returnFunctionPrefix}_{functionName}:")
    
    # Limpiar registros y descriptores que fueron modificados en la función (saliendo región ambigua)
    # Al salir de una función se debe considerar que todos los registros fueron vaciados
    self.freeAllRegisters()
    
    # Mover $sp a $fp
    self.addAssemblyCode(f"move $sp, $fp")
    
    # Hacer pop de frame pointer anterior
    self.addAssemblyCode(f"lw $fp, 0($sp)  # Hacer pop de frame pointer anterior")
    self.addAssemblyCode(f"addu $sp, $sp, 4")
    
    # Hacer pop de function level
    self.addAssemblyCode(f"addu $sp, $sp, 4  # Hacer pop de function level")
    
    # Hacer pop de retorno
    self.addAssemblyCode(f"lw $ra, 0($sp)  # Hacer pop de dirección de retorno")
    self.addAssemblyCode(f"addu $sp, $sp, 4")
      
    
    # Hacer pop de argumentos
    if numParams > 4:
      storedParams = numParams - 4
      self.addAssemblyCode(f"addu $sp, $sp, {storedParams * 4} # Hacer pop de argumentos")
    
    # Retornar a dirección de retorno
    self.addAssemblyCode(f"jr $ra")    
    
    # Añadir salto para evitar que se ejecute el código de la función fuera de una llamada
    self.addAssemblyCode(f"{skipFunctionPrefix}_{functionName}:")
    
    self.activeFunctions.pop() # Sacar función actual de funciones activas
    
    
  def translateGetArgInstruction(self, instruction):
    
    argNumber = int(instruction.arg1)
    totalArgs = int(instruction.arg2)
    destination = instruction.result
    
    # Para llegar al inicio del frame, se debe sumar el tamaño de $fp, functionLevel, $ra, 
    # y todos los argumentos del stack es decir 4 * (1 + 1 + 1 + totalArgs)
    
    # Calcular top position
    topPosition = 4 * (3 + totalArgs)
    
    # Calcular offset (se resta 4 incluso a argumento 0, pues el inicio del bloque es desde abajo)
    offset = topPosition - 4 * (argNumber + 1)
    
    self.addAssemblyCode(f"lw {compilerTemporary[0]}, {offset}($fp)  # Cargar argumento {argNumber}")
    self.addAssemblyCode(f"sw {compilerTemporary[0]}, {self.getOffset(destination)}({self.getBasePointer(destination)})  # Guardar argumento en destino")
    
  

  def translateReturnInstruction(self, instruction):
    
    value = instruction.arg1
    
    # Si el valor está en un registro, guardar en memoria
    valueAddr = self.addressDescriptor.getAddress(value)
    if isinstance(valueAddr, Register):
      self.saveRegisterValueInMemory(valueAddr, value)
    
    # Lo que se retorna es la dirección de memoria del heap
    # Cargar dirección de heap a $v1: los valores de funciones retornan siempre ahi
    self.addAssemblyCode(f"lw $v1, {self.getOffset(value)}({self.getBasePointer(value)})")
    
    # Saltar a la etiqueta de retorno
    currentFunctionName = self.activeFunctions[-1]
    self.addAssemblyCode(f"j {returnFunctionPrefix}_{currentFunctionName}")
    
  def translateCallInstruction(self, instruction):
    
    functionDef = instruction.arg1
    functionName = functionDef.getUniqueName()
    
    # Limpiar registros y descriptores pues variables podrían modificarse dentro de función
    self.freeAllRegisters()
    
    # Instruccion para realizar el salto a la función
    self.addAssemblyCode(f"jal {functionName}")
    
  def translateReturnValueInstruction(self, instruction):
    
    destination = instruction.result
    
    # Lo que se obtiene de $v1 es la dirección de memoria del heap
    # Se sobreescribe en la dirección de destination
    self.addAssemblyCode(f"sw $v1, {self.getOffset(destination)}({self.getBasePointer(destination)})")    
    
    # El nuevo valor está solo en memoria, no en registros.
    # Actualizar descriptores
    destAddresss = self.addressDescriptor.getAddress(destination)
    if isinstance(destAddresss, Register):
      # Guardar valor en memoria
      self.saveRegisterValueInMemory(destAddresss, destination)
      
      # Eliminar valor de destination en
      self.addressDescriptor.removeAddress(object=destination, address=destAddresss)
      self.registerDescriptor.removeValueFromRegister(register=destAddresss, value=destination)
    
    
  def translateParamInstruction(self, instruction):
    
    value = instruction.arg1
    
    # Obtener dirección de memoria del heap que contiene el valor
    self.addAssemblyCode(f"lw {compilerTemporary[0]}, {self.getOffset(value)}({self.getBasePointer(value)})")
    
    # Verificar si el último valor está en un registro, si lo está, guardar en memoria (heap)
    valueAddress = self.addressDescriptor.getAddress(value)
    if isinstance(valueAddress, Register):
      # Guardar valor de registro en heap memory
      # 4 de offset para saltar el tipo
      if valueAddress.type in (RegisterTypes.floatSaved, RegisterTypes.floatTemporary):
        self.addAssemblyCode(f"s.s {valueAddress}, 4({compilerTemporary[0]})")
        
      elif value.strictEqualsType((IntType, BoolType, NilType)):
        self.addAssemblyCode(f"sw {valueAddress}, 4({compilerTemporary[0]})")
        
      elif not value.strictEqualsType(StringType):
      
        # Obtener el tipo int o string en tiempo de ejecución
        self.addAssemblyCode(f"lb {compilerTemporary[1]}, 0({compilerTemporary[0]})")
        
        endStoreParamLabel = f"end_store_param_{getUniqueId()}"
        
        # Si es string no se guarda el valor, ya está en el heap
        self.addAssemblyCode(f"beq {compilerTemporary[1]}, {stringId}, {endStoreParamLabel}")
        
        # Alacenamiento int
        self.addAssemblyCode(f"sw {valueAddress}, 4({compilerTemporary[0]})")
        
        self.addAssemblyCode(f"{endStoreParamLabel}:")
    
    # Lo que se pasa no es el valor, sino la dirección de memoria del heap
    # Hacer push en el stack el parametro
    self.addAssemblyCode(f"subu $sp, $sp, 4  # Hacer push de argumento")
    self.addAssemblyCode(f"sw {compilerTemporary[0]}, 0($sp)")
    
  def translateMallocInstruction(self, instruction):
    
    size = int(instruction.arg1)
    destination = instruction.result
    
    # Reservar memoria en heap. +4 para guardar el tipo
    address = self.createHeapMemory(size + 4, destination)
    
    self.saveTypeInHeapMemory(intId, address)