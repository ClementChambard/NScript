import nsh.type_ as type_

import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from lexer import TOKEN
import lexer
import logger
import fileData as file
import primitives
import parseUtil as pu

    # should check for duplicate field name
@pu.useContext
def parseField():
    tokens = pu.Next()
    skip = 3

    if not pu.Check(TOKEN.IDENT): 
        logger.error(pu.Tok(), "Expected field type")
        return type_.FieldERROR

    typ = pu.Tok().val
    # check if correct type
    if not primitives.exists(typ): 
        logger.error(pu.Last(), f"{pu.Last().val} is not a valid type name")
        typ = "__ERROR__"

    if not pu.Check(TOKEN.IDENT): 
        logger.error(pu.Tok(False), "Expected identifier")
        return type_.FieldERROR

    name = pu.Tok().val
    cppName = name
    default = 0; 
    if typ != "__ERROR__": default = primitives.getType(typ).default

    if pu.CheckOpt(TOKEN.SYMBOL, "@"):
        if not pu.Check(TOKEN.IDENT): 
            logger.error(pu.Tok(False), "Expected identifier after symbol: @")
            return type_.FieldERROR
        cppName = pu.Tok().val
    if pu.CheckOpt(TOKEN.SYMBOL, "="):
        # should check expression
        if (typ == "error"):
            pu.Skip()
            logger.note(pu.Last(), "default value set here")
        else:
            if not pu.Check(primitives.getType(typ).token):
                logger.error(pu.Tok(skip=False), "wrong type for default value")
            default = pu.Tok().val
    if not pu.CheckSkip(TOKEN.SYMBOL, ";"): 
        logger.error(pu.Last(), "Expected symbol: ;")
        return type_.FieldERROR
    return type_.Field(typ, name, cppName, default)
    
@pu.useContext
def parseType():
    if not pu.CheckSkip(TOKEN.KEYWORD, "type"): 
        logger.error(pu.Tok(False), "Expected keyword: type")
        return type_.TypeERROR

    if not pu.Check(TOKEN.IDENT): 
        logger.error(pu.Tok(False), "Expected identifier after keyword: type")
        return type_.TypeERROR

    typename = pu.Tok().val
    cppName = typename
    fields = []

    if pu.CheckOpt(TOKEN.SYMBOL, "@"):
        if not pu.Check(TOKEN.IDENT): 
            logger.error(pu.Tok(False), "Expected identifier after symbol: @")
            return type_.TypeERROR
        cppName = pu.Tok().val
    if not pu.CheckSkip(TOKEN.SYMBOL, "{"): 
        logger.error(pu.Tok(False), "Expected symbol: {")
        return type_.TypeERROR
    while not pu.CheckOpt(TOKEN.SYMBOL, "}"): 
        if pu.Check(TOKEN.EOF):
            logger.error(pu.Tok(False), "Unexpected EOF")
            return type_.TypeERROR
        fields.append(parseField())
    return type_.Type(typename, cppName, fields)

@pu.useContext
def f():
    ts = []
    while not pu.Check(TOKEN.EOF):
        ts.append(parseType())
    return ts


def parseAll():
    tokens = lexer.lexAll(file.content)
    lexError = False
    for t in tokens:
        if (t.typ == TOKEN.ERROR):
            lexError = True
            logger.error(t, "unknown token")

    if lexError: return []

    typ = f(tokens=tokens)

    if file.errors > 0:
        print (f"{file.errors} errors occured")
        exit(1)

    for t in typ:  print(t)

    return typ
