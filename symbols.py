#!/usr/bin/env python3

from pointers import createPointer, addPointer
from dataType import getTypeStr
from instructions import checkVar, checkIns, checkValue, getVar, getIns, getValue, getInsArgs
from expression import getInsExpr, checkSimpleOp
from utils import ListFlatten, ThrowError

class Symbole:
    def __init__(self, string, line, column):
        self.sym = string
        self.line = line
        self.column = column
    def __str__(self):
        return filename + ":" + str(self.line) + ":" + str(self.column) + "   " + self.sym
    def parseString(self):
        if self.sym[0] != '"':
            return self.sym
        string = self.sym.strip('"')
        return string
    def parseNumber(self):
        if "." in self.sym and self.sym.replace(".","").isnumeric(): return float(self.rym)
        elif self.sym.isnumeric(): return int(self.sym)
        else: return -999999

def translateChar(symb):
    symb = symb.strip("'")
    if len(symb) > 1:
        if symb[0] != '\\': return -1
        if len(symb) > 2:
            print("CHAR > 2 NOT IMPLEMENTED")
            return -1
        if symb[1] == 'n': return str(ord('\n'))
        elif symb[1] == 't': return str(ord('\t'))
        elif symb[1] == 'r': return str(ord('\r'))
        elif symb[1] == 'f': return str(ord('\f'))
        elif symb[1] == 'a': return str(ord('\a'))
        elif symb[1] == 'b': return str(ord('\b'))
        elif symb[1] == '"': return str(ord('"'))
        elif symb[1] == "'": return str(ord("'"))
        elif symb[1] == '\\': return str(ord('\\'))

    return str(ord(symb))


L = 0
C = 0
currentSymbole = ""
currentSymboleL = L
currentSymboleC = C
symboles = []
def readContent(lines, firstline):
    global L, C, currentSymbole, currentSymboleC, currentSymboleL, symboles
    L = firstline
    C = 0
    currentSymbole = ""
    currentSymboleL = L
    currentSymboleC = C
    symboles = []
    slashMode = False
    blashMode = False
    stringMode = False
    charMode = False
    numberMode = False
    numberModeHasDecimal = False
    nameMode = False
    lineCommentMode = False
    commentMode = False
    commentModeStarMode = False


    def submit():
        global currentSymbole, currentSymboleL, currentSymboleC, symboles
        if currentSymbole == "": return
        symboles.append(Symbole(currentSymbole, currentSymboleL, currentSymboleC))
        currentSymbole = ""
        currentSymboleL = -1
        currentSymboleC = -1

    def addChar(c):
        global currentSymbole, currentSymboleL, currentSymboleC
        if currentSymbole == "":
            currentSymboleL = L
            currentSymboleC = C
        currentSymbole += c

    #def strL(x):
    #    s = str(x)
    #    if x < 10:
    #        return s + " "
    #    return s

    for c in lines:
        #print("char:", (' '+c,'\\n')[c=='\n'], "at ", str(L)+":"+str(C), "  slash:", int(slashMode), "  comment:", int(commentMode or lineCommentMode),\
        #      "   string:", int(stringMode), "   star:", int(commentModeStarMode), "   Symbole:",currentSymbole)

        # IF NEWLINE, CHANGE L AND C, RESET LINE COMMENTS AND CHAR MODES
        if c == '\n':
            if slashMode:
                C -= 1
                addChar('/')
                slashMode = False
            L += 1
            C = 0
            lineCommentMode = False
            commentModeStarMode = False
            submit()
            if stringMode:
                #error : no return in string
                return
            continue

        if lineCommentMode: continue
        if commentMode:
            if commentModeStarMode and c == '/':
                commentMode = False
            commentModeStarMode = c == '*'
            C += 1
            continue

        if slashMode:
            slashMode = False
            if c == '/':
                lineCommentMode = True
                C += 1
                continue
            elif c == '*':
                commentMode = True
                C += 1
                continue
            elif c != '/' and c != '*':
                C -= 1
                addChar('/')
                C += 1

        # STRINGS TAKE ALL CHARACTERS
        if stringMode:
            if c == '\\' and not blashMode:
                blashMode = True
            elif c == '"':
                addChar(c)
                if not blashMode:
                    submit()
                    stringMode = False
                else: blashMode = False
            elif blashMode:
                addChar('\\')
                addChar(c)
                blashMode = False
            else:
                addChar(c)
            C += 1
            continue

        # CHAR TRY TO TAKE ALL CHARACTERS
        if charMode:
            if c == '\\' and not blashMode:
                blashMode = True
            elif c == '\'':
                addChar(c)
                if not blashMode:
                    currentSymbole = translateChar(currentSymbole)
                    submit()
                    charMode = False
                else: blashMode = False
            elif blashMode:
                addChar('\\')
                addChar(c)
                blashMode = False
            else:
                addChar(c)
            C += 1
            continue

        # IF SPACE CHAR, ADD IT IF IN A STRING, CONTINUE OTHERWISE
        if c.isspace():
            if stringMode:
                addChar(c)
            elif currentSymbole != "":
                submit()
                slashMode = False
                stringMode = False
                numberMode = False
                numberModeHasDecimal = False
                nameMode = False
                lineCommentMode = False
                commentMode = False
                commentModeStarMode = False
            C += 1
            continue

        # IF ALPHANUMERIC CHAR OR UNDERSCORE, ADD IT
        if nameMode:
            if c.isalnum() or c == "_":
                addChar(c)
                C += 1
                continue
            else:
                nameMode = False
                submit()

        if numberMode:
            if c.isdigit():
                addChar(c)
                C += 1
                continue
            elif c == ".":
                if numberModeHasDecimal:
                    ThrowError("duplicate decimal point", L, C)
                addChar(c)
                C += 1
                numberModeHasDecimal = True
                continue

        if c == "/":
            submit()
            slashMode = True
            C += 1
            continue

        if c.isdigit() or c == "." or c =="-":
            if c == ".":
                numberModeHasDecimal = True
            addChar(c)
            numberMode = True
            C += 1
            continue

        if c.isalpha() or c == "_":
            addChar(c)
            nameMode = True
            C += 1
            continue

        # IF QUOTE, SUBMIT AND START A STRING, END A STRING IF ALLREADY IN ONE
        if c == '"':
            submit()
            stringMode = True
            addChar(c)
            C += 1
            continue

        if c == '\'':
            submit()
            charMode = True
            addChar(c)
            C += 1
            continue

        submit()
        addChar(c)
        submit()
        C += 1

    return symboles

instructionCount = 0
time = 0
labels = []

def findLabel(la):
    for l in labels:
        if l[0] == la:
            return l[1]
    return -1


def resolveLabel(symboles):
    global time, labels
    Plus = False
    Minus = False
    if len(symboles) > 3:
        ThrowError("Too much before label marker ':'", symboles[2].line, symboles[2].colum)
    elif len(symboles) == 1:
        ThrowError("Missing label name or time before ':'", symboles[0].line, symboles[0].column)
    elif len(symboles) == 3:
        if symboles[0].sym == '+': Plus = True
        elif symboles[0].sym == '-': Minus = True
        else: ThrowError("unknown symbole", symboles[0].line, symboles[0].column, len(symboles[0].sym))
        symboles = symboles[1:]
    if symboles[0].sym.isdigit():
        if Plus: time += int(symboles[0].sym)
        elif Minus: time -= int(symboles[0].sym)
        else: time = int(symboles[0].sym)
    else:
        if Plus or Minus: ThrowError("Can't use '+' or '-' before position label", symboles[0].line, symboles[0].column)
        createPointer(symboles[0].sym, instructionCount)
        #labels.append((symboles[0].sym, instructionCount))

def resolveIns(symboles, ins):
    global time, instructionCount
    if len(symboles) == 0: return
    Type = symboles[0].sym
    Args = symboles[1:-1]
    cur_ins_args = []
    cur_ins_args_type = []
    if checkVar(Type):
        symboles.pop()
        return resolveExpr(symboles, ins)
    elif checkIns(Type):
        for s in Args:
            l = findLabel(s.sym)
            if l != -1:
                cur_ins_args.append(str(l))
                cur_ins_args_type.append("S")
                continue
            t = ("S","f")['.' in s.sym]
            if checkVar(s.sym):
                s.sym, t = getVar(s.sym)
                s.sym = str(s.sym)
            elif checkValue(s.sym):
                s.sym = getValue(s.sym)
                t = ("S","f")['.' in s.sym]
                s.sym = str(s.sym)
            cur_ins_args.append(s.parseString())
            cur_ins_args_type.append(t)
        nT = getIns(Type, cur_ins_args_type)
        if nT == -1:
            ThrowError(f"wrong argument type {cur_ins_args_type} for function {Type}", symboles[0].line, symboles[0].column, len(symboles[0].sym))
        # cast arguments
        at = getInsArgs(nT)
        for i in range(len(at)):
            if at[i] == 'S': cur_ins_args[i] = str(int(float(cur_ins_args[i])))
            elif at[i] == 'f': cur_ins_args[i] = str(float(cur_ins_args[i]))
        Type = nT
    else:
        ThrowError(f"unknown instruction {Type}", symboles[0].line, symboles[0].column, len(symboles[0].sym))
    ins.append((Type, time, cur_ins_args, instructionCount))
    instructionCount += 8 + 4 * len(cur_ins_args)

def resolveExpr(symboles, ins):
    global time, instructionCount

    abort = lambda : ThrowError("unresolvable expression", symboles[0].line, symboles[0].column, 0)

    varAffect , t = getVar(symboles[0].sym)
    if len(symboles) == 0: return
    for i in range(len(symboles)):
        if checkVar(symboles[i].sym):
            symboles[i] , _ = getVar(symboles[i].sym)
            symboles[i] = str(symboles[i])
        elif checkValue(symboles[i].sym):
            symboles[i] = getValue(symboles[i].sym)
            symboles[i] = str(symboles[i])
        else:
            symboles[i] = symboles[i].sym

    newins, instructionCount = checkSimpleOp(symboles, t, time, instructionCount)
    if newins != -1:
        ins.append(newins)
    else:
        eq = symboles[1]
        if not '=' in eq: abort()
        newins, instructionCount = getInsExpr(symboles[2:], t, time, instructionCount)
        ins += newins
        ins.append(((104,105)[t=="f"], time, [varAffect], instructionCount))
        instructionCount += 12

def resolveBackInstrs(lastInstr, firstInstr, block):
    global instructionCount, time
    if type(lastInstr) == str:
        if lastInstr == "IF ENDS HERE":
            firstInstr[-1][2][0] = instructionCount
            firstInstr[-1][2][1] = time
        return firstInstr + block
    else:
        return firstInstr + block + lastInstr

def resolveCodeBlock(symboles, first, guardSymboles = []):
    global instructionCount, time
    block = []
    last_symboles = []
    firstInstr = []
    lastInstr = []

    def evalExpr(expr):
        global instructionCount, time
        for i in range(len(expr)):
            if checkVar(expr[i].sym):
                expr[i] , _ = getVar(expr[i].sym)
                expr[i] = str(expr[i])
            else:
                expr[i] = expr[i].sym

        # TODO: test if it's a simple case
        newins, instructionCount = getInsExpr(expr, "S", time, instructionCount)
        return newins


    if guardSymboles != []:
        t = guardSymboles[0]
        guardSymboles = guardSymboles[1:]
        if t.sym == "if":
            if guardSymboles[0].sym != '(' or guardSymboles[-1].sym != ')':
                ThrowError("NO ()", guardSymboles[0].l, guardSymboles[0].c, len(guardSymboles[0].sym))
            firstInstr += evalExpr(guardSymboles[1:-1])
            firstInstr.append((215, time, [0, 0], instructionCount))
            instructionCount += 16

            lastInstr = "IF ENDS HERE"

    i = first
    while i < len(symboles):
        s = symboles[i]
        if s.sym == ';':
            last_symboles.append(s)
            resolveIns(last_symboles, block)
            last_symboles = []
        elif s.sym == ':':
            last_symboles.append(s)
            resolveLabel(last_symboles)
            last_symboles = []
        elif s.sym == '{':
            b, i = resolveCodeBlock(symboles, i+1, last_symboles)
            block.append(b)
            last_symboles = []
        elif s.sym == '}':
            return resolveBackInstrs(lastInstr, firstInstr, block), i
        else:
            last_symboles.append(s)

        i += 1
    return resolveBackInstrs(lastInstr, firstInstr, block)

def updateIns(ins):
    insList = list(ins)
    insList[2] = [[a, getTypeStr(a)] for a in insList[2]]
    for a in insList[2]:
        if a[1] == 'str':
            a[0] = addPointer(a[0])
            a[1] = 'ptr'
        elif a[1] == "S": a[0] = int(a[0])
        elif a[1] == "f": a[0] = float(a[0])
    return insList

def getScriptIns(symboles):
    ins_bloc = resolveCodeBlock(symboles, 0)
    #print (ins_bloc) # __DEBUG__
    return [updateIns(i) for i in ListFlatten(ins_bloc)]
