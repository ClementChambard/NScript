import os
import stat
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from cache.cache_util import fileChanged
from nsh.type_ import Type

class CacheTypeField:
    def __init__(self, *args):
        if len(args) == 1:
            self.typ = args[0].typ
            self.name = args[0].name
            self.cpp = args[0].cpp
            self.default = args[0].default
        else:
            self.typ = args[0]
            self.name = args[1]
            self.cpp = args[2]
            self.default = args[3]

class CacheType:
    def __init__(self, name: str, cpp: str, fields = [], toParse = []):
        self.name = name
        self.cpp = cpp
        self.fields = [CacheTypeField(f) for f in fields]
        for i in range(0,len(toParse), 4):
            self.fields.append(CacheTypeField(toParse[i],toParse[i+1],toParse[i+2],toParse[i+3]))

    def save(self):
        buf = self.name + " " + self.cpp + " " + str(len(self.fields)) + " "
        for f in self.fields: buf += f.typ + " " + f.name + " " + f.cpp + " " + f.default + " "
        return buf

    def hasChanged(self, t: Type, CACHE):
        if fileChanged(self.cpp + ".hpp", CACHE.file(self.cpp + ".hpp").timestamp): return True
        if t.cpp != self.cpp:
            #TODO: remove old file
            return True
        if len(t.fields) != len(self.fields): return True
        for t,f in zip(self.fields, t.fields):
            if t.typ != f.typ: return True
            if t.name != f.name: return True
            if t.cpp != f.cpp: return True
            if t.default != f.default: return True
        return False

    def update(self, t: Type):
        self.name = t.name
        self.cpp = t.cpp
        self.fields = [CacheTypeField(f) for f in t.fields]
