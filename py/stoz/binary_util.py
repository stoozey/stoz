def int_get_byte_length(x: int) -> int:
    return ((x.bit_length() + 7) // 8)

def int_to_bytes(x: int) -> bytes:
    return x.to_bytes(int_get_byte_length(x), 'big')

def int_from_bytes(x: bytes) -> int:
    return int.from_bytes(x, 'big')
