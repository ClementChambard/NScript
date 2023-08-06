#!/usr/bin/env python3


class COL:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINKSLOW = "\033[5m"
    BLINKFAST = "\033[6m"
    INVERT = "\033[7m"
    INVISIBLE = "\033[8m"
    STROKE = "\033[9m"
    NOBOLD = "\033[22m"
    NOITALIC = "\033[23m"
    NOUNDERLI = "\033[24m"
    NOBLINK = "\033[25m"
    NOINVERT = "\033[27m"
    NOINVISI = "\033[28m"
    NOSTROKE = "\033[29m"
    FG_BLACK = "\033[30m"
    FG_RED = "\033[31m"
    FG_GREEN = "\033[32m"
    FG_YELLOW = "\033[33m"
    FG_BLUE = "\033[34m"
    FG_PURPLE = "\033[35m"
    FG_CYAN = "\033[36m"
    FG_WHITE = "\033[37m"
    FG_RESET = "\033[39m"
    BLACK = "\033[90m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    def setFG_rgb(r, g, b):
        return "\033[38;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"

    def setFG(n):
        return "\033[38;5;" + str(n) + "m"


filename = ""
fileContent = ""

from os.path import exists
import json


def readFile(f):
    global filename, fileContent
    filename = f
    if not exists(f):
        print("not a file")
        exit(1)
    with open(filename, "r") as opened_source_file:
        for l in opened_source_file:
            fileContent += l
    return fileContent


def getFilename():
    return filename


def getCurrentMeta(f):
    meta = []
    if exists(f):
        with open(f, "r") as f:
            for l in f:
                meta.append(json.loads(l))
    return meta


def strIsInt(s):
    if s.isnumeric():
        return True
    if s[0] == "-" or s[0] == "+":
        return strIsInt(s[1:])


def OctToInt(o):
    v = 0
    for c in o:
        v *= 8
        try:
            v += int(c)
        except:
            print("error with num", c)
    return v


def HexToIntDigit(c):
    try:
        return int(c)
    except:
        if c.lower() == "a":
            return 10
        if c.lower() == "b":
            return 11
        if c.lower() == "c":
            return 12
        if c.lower() == "d":
            return 13
        if c.lower() == "e":
            return 14
        if c.lower() == "f":
            return 15


def HexToInt(st):
    v = 0
    for c in st:
        v *= 16
        v += HexToIntDigit(c)
    return v


def HexDigit(n):
    if n < 10:
        return str(n)
    elif n == 10:
        return "A"
    elif n == 11:
        return "B"
    elif n == 12:
        return "C"
    elif n == 13:
        return "D"
    elif n == 14:
        return "E"
    elif n == 15:
        return "F"


def intTo4digitHex(invar):
    outvar = ""
    for _ in range(4):
        outvar = HexDigit(invar % 16) + outvar
        invar //= 16
    return "0x" + outvar


def ListFlatten(l):
    out = []
    for e in l:
        if type(e) == list:
            out = out + ListFlatten(e)
        else:
            out.append(e)
    return out


def indentListOfList(l, i=0):
    ind = i * 4 * " "
    for e in l:
        if type(e) == list:
            print(ind + "[")
            indentListOfList(e, i + 1)
            print(ind + "],")
        else:
            print(ind + str(e) + ",")


READ_LOCATION = ""


def setReadLocation(loc):
    global READ_LOCATION
    READ_LOCATION = loc


def ShowLocation():
    line = COL.BOLD + filename + ": " + COL.RESET + READ_LOCATION + " :"
    print(line)


def terminateCompilation():
    print("compilation terminated")
    exit(1)


def ThrowError(error, l, c, length=1):
    nbspaces = 5 - len(str(l + 1))
    codeLine = ""
    for i, ch in enumerate(fileContent.split("\n")[l]):
        if i == c:
            codeLine += COL.setFG_rgb(1) + COL.BOLD
        if i == c + length:
            codeLine += COL.RESET
        codeLine += ch
    firstLine = (
        COL.BOLD
        + filename
        + ":"
        + str(l + 1)
        + ":"
        + str(c)
        + ": "
        + COL.setFG_rgb(1)
        + "error: "
        + COL.RESET
        + error
    )
    secondLine = nbspaces * " " + str(l + 1) + " | " + codeLine
    thirdLine = (
        "      | "
        + c * " "
        + COL.setFG_rgb(1)
        + COL.BOLD
        + "^"
        + max(0, length - 1) * "~"
        + COL.RESET
    )
    ShowLocation()
    print(firstLine)
    print(secondLine)
    print(thirdLine)
    terminateCompilation()
