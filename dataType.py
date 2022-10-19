#!/usr/bin/env python3

from integerType import *
from floatType import *
from stringType import *
from utils import strIsInt

DATATYPES = [
    ("S", int),
    ("f", float),
    ("str", str),
    ("NULL", -1)
]

def checkType(v):
    for t in DATATYPES:
        if type(v) == t[1]:
            return t[0]
    return "NULL"

def getTypeStr(v):
    if type(v) == str:
        if "." in v:
            v2 = v.replace('.','')
            if strIsInt(v2):
                return "f"
        elif strIsInt(v): return "S"
        else: return "str"
    else:
        return checkType(v)
