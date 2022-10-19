#!/usr/bin/env python3

from utils import intTo4digitHex
from stringType import writeString, escapeString

# Pointers are the links in the compiled code
# Ptr => [val, id, addr, isStr]
pointers = []
NULLPTR = -1
PTR_VALUE = 0
PTR_ID = 1
PTR_ADDR = 2
PTR_WRITE = 3

PTR_DEBUG = False

def setPtrDebug(val):
    global PTR_DEBUG
    PTR_DEBUG = val

def resetPointers():
    global pointers
    if PTR_DEBUG: print("\033[93m<DEBUG>\033[0m [POINTERS] resetting pointers")
    pointers = []

def addPointer(val):
    for p in pointers:
        if val == p[PTR_VALUE]:
            return p[PTR_ID]
    if PTR_DEBUG: print(f"\033[93m<DEBUG>\033[0m [POINTERS] Added ptr {len(pointers)} of value '{val}' at adress NULLPTR (added)")
    pointers.append([val, len(pointers), NULLPTR, True])
    return len(pointers) -1

def createPointer(val, pos):
    for p in pointers:
        if val == p[PTR_VALUE]:
            if (not p[PTR_WRITE] or p[PTR_ADDR] != NULLPTR):
                print("\033[91m<ERROR>\033[0m [POINTERS] error creating pointer :", val)
                return
            else:
                if PTR_DEBUG: print(f"\033[93m<DEBUG>\033[0m [POINTERS] Moved ptr {p[PTR_ID]} of value '{val}' to adress {intTo4digitHex(pos)} (created)")
                p[PTR_ADDR] = pos
                p[PTR_WRITE] = False
                return
    if PTR_DEBUG: print(f"\033[93m<DEBUG>\033[0m [POINTERS] Added ptr {len(pointers)} of value '{val}' at adress {intTo4digitHex(pos)} (created)")
    pointers.append([val, len(pointers), pos, False])


def getPtrValue(i):
    return pointers[i][PTR_VALUE]

def getPtrAddr(i):
    return pointers[i][PTR_ADDR]

def affectPtrs(offset):
    for p in pointers:
        if p[PTR_WRITE]:
            p[PTR_ADDR] = offset
            offset += len(p[PTR_VALUE]) + 1
            if PTR_DEBUG: print(f"\033[93m<DEBUG>\033[0m [POINTERS] Moved ptr {p[PTR_ID]} of value '{p[PTR_VALUE]}' to adress {intTo4digitHex(p[PTR_ADDR])} (affected)")

def writePtrs(f):
    if PTR_DEBUG: print("\033[93m<DEBUG>\033[0m [POINTERS] Writing pointers")
    for p in pointers:
        if not p[PTR_WRITE]: continue
        writeString(f, escapeString(p[PTR_VALUE]))

def asmPtrs():
    out = ""
    if PTR_DEBUG: print("\033[93m<DEBUG>\033[0m [POINTERS] Asemble pointers")
    for p in pointers:
        if not p[PTR_WRITE]: continue
        out += intTo4digitHex(p[PTR_ADDR]) + ' ' + str(p[PTR_VALUE]) + '\n'
    return out

def resolvePtrs(sub):
    if PTR_DEBUG: print("\033[93m<DEBUG>\033[0m [POINTERS] Resolving pointers")
    for i in sub:
        for a in i[2]:
            if a[1] == 'ptr':
                a[0] = getPtrAddr(a[0])
