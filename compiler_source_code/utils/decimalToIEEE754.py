import struct

def decimal_to_ieee754(num):
    # Convierte el número decimal a su representación en IEEE 754 de 32 bits
    packed = struct.pack('!f', float(num))  # Empaqueta el número como un float de 32 bits
    # Convierte a entero sin signo y luego a hexadecimal
    hex_representation = ''.join(f'{byte:02x}' for byte in packed)
    return "0x" + hex_representation.upper()
