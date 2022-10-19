#!/usr/bin/env python3

from utils import *

def StringError(err):
    print(err)
    return "INVALID_STRING : \""+err+"\""

def escapeString(inp):
    if type(inp) != str:
        return StringError("escapeString : input is not a string")
    out = ""
    backslash = False
    octal = False
    hexa = False
    uni = False
    Uni = False
    name = False
    charname = ""
    nums = ""
    for c in inp:
        if backslash:
            if c == "\\": out += "\\"
            elif c == "'": out += "'"
            elif c == "\"": out += "\""
            elif c == "a": out += "\a"
            elif c == "b": out += "\b"
            elif c == "n": out += "\n"
            elif c == "f": out += "\f"
            elif c == "t": out += "\t"
            elif c == "r": out += "\r"
            elif c == "x": hexa = True
            elif c == "N": name = True
            elif c == "u": uni = True
            elif c == "U": Uni = True
            elif c.isnumeric():
                octal = True
                nums += c
            backslash = False
            continue
        if c == "\\":
            backslash = True
            continue
        if octal:
            if len(nums) == 3:
                octal = False
                out += chr(OctToInt(nums))
                nums = ""
            else:
                nums += c
            continue
        if hexa:
            if len(nums) == 2:
                hexa = False
                out += chr(HexToInt(nums))
                nums = ""
            else:
                nums += c
            continue
        if uni:
            if len(nums) == 4:
                hexa = False
                out += chr(HexToInt(nums))
                nums = ""
            else:
                nums += c
            continue
        if Uni:
            if len(nums) == 8:
                hexa = False
                out += chr(HexToInt(nums))
                nums = ""
            else:
                nums += c
            continue

        out += c

    return out

def writeString(f, s):
    for c in s:
        if ord(c) > 255:
            print("long unicode char not implemented")
            assert False
        else:
            f.write(ord(c).to_bytes(1, byteorder='little'))
    f.write((0).to_bytes(1, byteorder='little'))
