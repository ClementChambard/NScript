#!/usr/bin/env python3

from symbols import readContent
from utils import ThrowError, filename, getCurrentMeta

currentHeader = -1


""" ALIAS SYSTEM """

ALIAS_KEY_WORD = -1
ALIAS_TYPE_KEYWORD_POS = -1
ALIAS_NAME_SYMBOLE_POS = -1
ALIAS_VALUE_SYMBOLE_POS = -1
ALIAS_OTHER_SYMBOLES = -1
ALIAS_SYNTAX_LENGTH = -1
ALIAS_TYPES = []
ALIAS_DEBUG = False
ALIAS_ENABLE = False

def aliasAddType(name, keywords, setFunc = lambda x, y : 1, checkFunc = lambda x : True):
    ALIAS_TYPES.append((keywords, checkFunc, setFunc, name))

def aliasSetExpr(regexp):
    global ALIAS_KEY_WORD, ALIAS_OTHER_SYMBOLES, ALIAS_SYNTAX_LENGTH, ALIAS_NAME_SYMBOLE_POS, ALIAS_TYPE_KEYWORD_POS, ALIAS_VALUE_SYMBOLE_POS
    regexp = regexp.split()
    ALIAS_KEY_WORD = regexp[0]
    ALIAS_OTHER_SYMBOLES = []
    ALIAS_SYNTAX_LENGTH = len(regexp) - 1
    for i in range(1, len(regexp)):
        if   regexp[i] == '%n': ALIAS_NAME_SYMBOLE_POS  = i
        elif regexp[i] == '%t': ALIAS_TYPE_KEYWORD_POS  = i
        elif regexp[i] == '%v': ALIAS_VALUE_SYMBOLE_POS = i
        else: ALIAS_OTHER_SYMBOLES.append((i, regexp[i]))

def aliasSetDebug(boolean):
    global ALIAS_DEBUG
    ALIAS_DEBUG = boolean

def aliasEnable(boolean):
    global ALIAS_ENABLE
    ALIAS_ENABLE = boolean

def checkAliasStruct(symboles, i):
    if symboles[i].sym == ALIAS_KEY_WORD:
        if i+ALIAS_SYNTAX_LENGTH >= len(symboles):
            ThrowError("incomplete alias declaration", symboles[i].line, symboles[i].column, len(symboles[i].sym))
        for s in ALIAS_OTHER_SYMBOLES:
            if symboles[i+s[0]].sym != s[1]:
                if ALIAS_DEBUG: print (s[1], symboles[i+s[0]].sym)
                ThrowError(f"expected symbol '{s[1]}'", symboles[i+s[0]].line, symboles[i+s[0]].column, len(symboles[i+s[0]].sym))
        aliasName = symboles[i+ALIAS_NAME_SYMBOLE_POS]
        aliasVal = symboles[i+ALIAS_VALUE_SYMBOLE_POS]
        for t in ALIAS_TYPES:
            if symboles[i+ALIAS_TYPE_KEYWORD_POS].sym in t[0]:
                if not t[1](aliasVal.sym):
                    ThrowError(f"expected {t[3]} name for alias", aliasVal.line, aliasVal.column, len(symboles[i+ALIAS_VALUE_SYMBOLE_POS].sym))
                if t[2](aliasVal.sym, aliasName.sym) < 0: ThrowError(f"name {alias} is already used", aliasName.line, aliasName.column, len(symboles[i+ALIAS_NAME_SYMBOLE_POS].sym))
                if ALIAS_DEBUG: print(f"\033[93m<DEBUG>\033[0m [ALIASES] Added {t[3]} alias {aliasName.sym} for value {aliasVal.sym}")
                break
        else: ThrowError(f"incorrect alias type {symboles[i+ALIAS_TYPE_KEYWORD_POS].sym}", symboles[i+ALIAS_TYPE_KEYWORD_POS].line, symboles[i+ALIAS_TYPE_KEYWORD_POS].column, len(symboles[i+ALIAS_TYPE_KEYWORD_POS].sym))
        return ALIAS_SYNTAX_LENGTH
    else:
        return 0



""" META SYSTEM """

import json

def checkMetaStruct(symboles, i, meta):
    if len(symboles) <= i+2 or symboles[i+1].sym != ":":
        return 0
    metaName = symboles[i].sym
    metaVal = symboles[i+2].sym.strip('"')
    if metaVal == symboles[i+2].sym:
        ThrowError(f"expected string for field '{metaName}'", symboles[i+2].line, symboles[i+2].column, len(symboles[i+2].sym))
    meta[metaName] = metaVal
    return 2

def writeHeaderMetaFile(h, f, f2, f3):
    headerMeta = h.meta
    headerMeta["file_name"] = f2
    headerMeta["origin_file"] = f3
    currentMeta = getCurrentMeta(f)
    removeVals = []
    for m in currentMeta:
        if m["file_name"] == headerMeta["file_name"] or \
           m["script_name"] == headerMeta["script_name"] or \
           m["origin_file"] == headerMeta["origin_file"]:
            removeVals.append(m)
    for v in removeVals:
        currentMeta.remove(v)
    currentMeta.append(headerMeta)
    metaLines = [json.dumps(m)+"\n" for m in currentMeta]
    with open(f, 'w') as f:
        f.writelines(metaLines)

""""
    ScriptHeader :
      - Has the task to parse the text outside subroutines
      - Contains the metadata of the script
"""
class ScriptHeader:

    def getCurrent():
        return currentHeader
    def setCurrent(text):
        global currentHeader
        currentHeader = ScriptHeader(text)
    def writeMeta(filename, compiledFileName, originFileName):
        writeHeaderMetaFile(currentHeader, filename, compiledFileName, originFileName)

    def __init__(self, text):
        self.meta = {}
        symboles = readContent(text, 0)
        skip = 0
        for i in range(len(symboles)):
            if skip > 0:
                skip -= 1
                continue

            if ALIAS_ENABLE: skip = checkAliasStruct(symboles, i);
            if skip > 0: continue
            skip = checkMetaStruct(symboles, i, self.meta)
            if skip > 0: continue
            ThrowError(f"unknown symbol {symboles[i].sym}", symboles[i].line, symboles[i].column, len(symboles[i].sym))

    def __str__(self):
        return str(self.meta)
