from lexer import TOKEN

class Primitive:
    def __init__(self, name: str, cpp: str, default: str, py, token: TOKEN):
        self.name = name
        self.cpp = cpp
        self.default = default
        self.py = py
        self.token = token

types = [
    Primitive("uint8" , "uint8_t"    , "0"   , int  , TOKEN.INT  ),
    Primitive("uint16", "uint16_t"   , "0"   , int  , TOKEN.INT  ),
    Primitive("uint32", "uint32_t"   , "0"   , int  , TOKEN.INT  ),
    Primitive("uint64", "uint64_t"   , "0"   , int  , TOKEN.INT  ),
    Primitive("int8"  , "int8_t"     , "0"   , int  , TOKEN.INT  ),
    Primitive("int16" , "int16_t"    , "0"   , int  , TOKEN.INT  ),
    Primitive("int32" , "int32_t"    , "0"   , int  , TOKEN.INT  ),
    Primitive("int64" , "int64_t"    , "0"   , int  , TOKEN.INT  ),
    Primitive("float" , "float"      , "0.f" , float, TOKEN.FLOAT),
    Primitive("string", "const char*", "\"\"", str  , TOKEN.STR  ),
    Primitive("script", "void*"      , "NULL", str  , TOKEN.IDENT),
]

def typeId(typename: str) -> int:
    for i, t in enumerate(types):
        if t.name == typename:
            return i
    return -1

def getType(typename: str) -> Primitive:
    for t in types:
        if t.name == typename:
            return t
    return []

def exists(typename: str) -> bool:
    for t in types:
        if t.name == typename:
            return True
    return False

def toCpp(typename: str) -> str:
    return getType(typename).cpp
