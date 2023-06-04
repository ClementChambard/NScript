import os
import sys
import time
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from primitives import toCpp

class Field:
    def __init__(self, typ: str, name: str, cpp: str, default: str):
        self.typ = typ
        self.name = name
        self.cpp = cpp
        self.default = default

    def to_cache(self):
        return self.typ + " " + self.name + " " + [self.cpp,"."][self.cpp==self.name] + " " + self.default + " "

    def to_hpp(self):
        return f"    {toCpp(self.typ)} {self.cpp} = {self.default};\n"

    def is_error(self):
        return self.typ == "__ERROR__" or self.name == "__ERROR__" or self.cpp == "__ERROR__" or self.default == "__ERROR__"

    def __str__(self):
        return f"{self.name}{['','@'+self.cpp][self.name != self.cpp]}:{self.typ}={self.default}"

FieldERROR = Field("__ERROR__", "__ERROR__", "__ERROR__", "__ERROR__")

class Type: 
    def __init__(self, name: str, cpp: str, fields: [Field]):
        self.name = name
        self.cpp = cpp
        self.fields = fields
        for f in fields:
            if f.is_error():
                self.name = "__ERROR__"
                self.cpp = "ErrorType"
                self.fields = []
                break

    def to_cache(self):
        out = f"TYPE {self.name} {self.cpp} {int(time.time())} {len(self.fields)} "
        for f in self.fields: out += f.to_cache()
        return out

    def to_hpp(self):
        out = ""
        out += f"#ifndef {self.cpp.upper()}_INCLUDED_H\n"
        out += f"#define {self.cpp.upper()}_INCLUDED_H\n"
        out +=  "\n"
        out +=  "#include <cstdint>\n"
        out +=  "\n"
        out += f"struct {self.cpp} {'{'}\n"
        for f in self.fields: out += f.to_hpp()
        out +=  "};\n"
        out +=  "\n"
        out += f"#endif //{self.cpp.upper()}_INCLUDED_H\n"
        return out

    def is_error(self):
        return self.name == "__ERROR__"

    def __str__(self):
        out = f"Type: {self.name}@{self.cpp} [ "
        for f in self.fields:
            out += str(f) + " "
        return out + "]"

TypeERROR = Type("__ERROR__", "ErrorType", [])

