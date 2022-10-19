#!/usr/bin/env python3

class insType:
    def __init__(self, num, name, argString):
        self.num = num
        self.name = name
        self.argString = argString
        self.aliases = []
    def addAlias(self, al):
        if not al in self.aliases:
            self.aliases.append(al)
            return True
        else: return False
    def getNumArgs(self):
        return len(self.argString)
    def getSize(self):
        return 8 + 4 * self.getNumArgs()
    def getFullName(self):
        return self.name + "(" + self.argString + ")"
    def match(self, matchStr):
        return matchStr == self.name or matchStr in self.aliases or matchStr == "ins_" + str(self.num)
    def matchArgs(self, matchStr, args):
        if not self.match(matchStr): return False
        if len(args) != len(self.argString): return False
        for i in range(len(args)):
            if args[i] != self.argString[i]: return False
        return True

INSTRUCTION_SET = [
    insType(0, "nop", ""),
    insType(1, "return", ""),
    insType(2, "call", "S"),
    insType(50, "puts", "S"),
    insType(51, "putc", "S"),
    insType(52, "put", "S"),
    insType(53, "put", "f"),
    insType(99, "dumpState", ""),

    insType(100, "set", "SS"),
    insType(101, "set", "ff"),
    insType(102, "push", "S"),
    insType(103, "push", "f"),
    insType(104, "pop", "S"),
    insType(105, "pop", "f"),
    insType(106, "add", "SS"),
    insType(107, "add", "ff"),
    insType(108, "sub", "SS"),
    insType(109, "sub", "ff"),
    insType(110, "mul", "SS"),
    insType(111, "mul", "ff"),
    insType(112, "div", "SS"),
    insType(113, "div", "ff"),
    insType(114, "mod", "SS"),
    insType(115, "mod", "ff"),
    insType(116, "setAdd", "SSS"),
    insType(117, "setAdd", "fff"),
    insType(118, "setSub", "SSS"),
    insType(119, "setSub", "fff"),
    insType(120, "setMul", "SSS"),
    insType(121, "setMul", "fff"),
    insType(122, "setDiv", "SSS"),
    insType(123, "setDiv", "fff"),
    insType(124, "setMod", "SSS"),
    insType(125, "setMod", "fff"),
    insType(126, "equals", "SSS"),
    insType(127, "equals", "Sff"),
    insType(128, "differ", "SSS"),
    insType(129, "differ", "Sff"),
    insType(130, "bigger", "SSS"),
    insType(131, "bigger", "Sff"),
    insType(132, "bigEq", "SSS"),
    insType(133, "bigEq", "Sff"),
    insType(134, "smaller", "SSS"),
    insType(135, "smaller", "Sff"),
    insType(136, "smallEq", "SSS"),
    insType(137, "smallEq", "Sff"),
    insType(138, "not", "SS"),
    insType(139, "and", "SSS"),
    insType(140, "or", "SSS"),
    insType(141, "xor", "SSS"),
    insType(142, "iadd", ""),
    insType(143, "fadd", ""),
    insType(144, "isub", ""),
    insType(145, "fsub", ""),
    insType(146, "imul", ""),
    insType(147, "fmul", ""),
    insType(148, "idiv", ""),
    insType(149, "fdiv", ""),
    insType(150, "imod", ""),
    insType(151, "fmod", ""),
    insType(152, "ieq", ""),
    insType(153, "feq", ""),
    insType(154, "ine", ""),
    insType(155, "fne", ""),
    insType(156, "igt", ""),
    insType(157, "fgt", ""),
    insType(158, "ige", ""),
    insType(159, "fge", ""),
    insType(160, "ilt", ""),
    insType(161, "flt", ""),
    insType(162, "ile", ""),
    insType(163, "fle", ""),
    insType(164, "not", ""),
    insType(165, "and", ""),
    insType(166, "or", ""),
    insType(167, "xor", ""),

    insType(200, "jump", "SS"),
    insType(201, "jumpDec", "SSS"),
    insType(202, "jumpEq", "SSSS"),
    insType(203, "jumpEq", "SSff"),
    insType(204, "jumpNeq", "SSSS"),
    insType(205, "jumpNeq", "SSff"),
    insType(206, "jumpGt", "SSSS"),
    insType(207, "jumpGt", "SSff"),
    insType(208, "jumpGe", "SSSS"),
    insType(209, "jumpGe", "SSff"),
    insType(210, "jumpLt", "SSSS"),
    insType(211, "jumpLt", "SSff"),
    insType(212, "jumpLe", "SSSS"),
    insType(213, "jumpLe", "SSff"),
    insType(214, "jumpSt", "SS"),
    insType(215, "jumpNotSt", "SS"),

    insType(300, "attack", "SSfffffff"),
    insType(301, "resetHitboxGroup", "S"),
    insType(302, "resetHitboxes", "S")
]

def addInsAlias(s, a):
    ret = -2
    for v in VARIABLE_SET:
        if a in v.aliases or a == v.name: return -1
    for i in INSTRUCTION_SET:
        if a in i.aliases or a == i.name: return -1
    for v in VALUES_SET:
        if a == v.name: return -1
    for i in INSTRUCTION_SET:
        if i.match(s):
            i.addAlias(a)
            ret = 0
    return ret

def checkIns(s):
    for i in INSTRUCTION_SET:
        if i.match(s): return True
    return False

def getIns(s, args):
    for i in INSTRUCTION_SET:
        if i.matchArgs(s, args): return i.num
    for i in INSTRUCTION_SET:
        if i.match(s): return i.num
    return -1

def getInsArgs(n):
    for i in INSTRUCTION_SET:
        if i.num == n:
            return i.argString
    return ""

class Variable:
    def __init__(self, num, name, t):
        self.num = num
        self.name = name
        self.Type = t
        self.aliases = []
    def addAlias(self, al):
        if not al in self.aliases:
            self.aliases.append(al)
            return True
        else: return False
    def match(self, matchStr):
        return matchStr == self.name or matchStr in self.aliases


VARIABLE_SET = [
    Variable("100000", "I0", "S"),
    Variable("100001", "I1", "S"),
    Variable("100002", "I2", "S"),
    Variable("100003", "I3", "S"),
    Variable("100004", "I4", "S"),
    Variable("100005", "I5", "S"),
    Variable("100006", "I6", "S"),
    Variable("100007", "I7", "S"),
    Variable("100008", "I8", "S"),
    Variable("100009", "I9", "S"),
    Variable("100010", "f0", "f"),
    Variable("100011.", "f1", "f"),
    Variable("100012.", "f2", "f"),
    Variable("100013.", "f3", "f"),
    Variable("100014.", "f4", "f"),
    Variable("100015.", "f5", "f"),
    Variable("100016.", "f6", "f"),
    Variable("100017.", "f7", "f"),
    Variable("100018.", "f8", "f"),
    Variable("100019.", "f9", "f"),
    Variable("100050", "Itop", "S"),
    Variable("100051.", "ftop", "f"),
]

def addVarAlias(s,a):
    for v in VARIABLE_SET:
        if a in v.aliases or a == v.name: return -1
    for i in INSTRUCTION_SET:
        if a in i.aliases or a == i.name: return -1
    for v in VALUES_SET:
        if a == v.name: return -1
    for v in VARIABLE_SET:
        if v.match(s): return (-1,0)[v.addAlias(a)]
    return -2

def checkVar(s):
    for v in VARIABLE_SET:
        if v.match(s): return True
    return False

def getVar(s):
    for v in VARIABLE_SET:
        if v.match(s): return v.num, v.Type
    return -1

class ValueAlias:
    def __init__(self, val, name):
        self.name = name
        self.val = val

VALUES_SET = [

]

def addValAlias(val, a):
    for v in VARIABLE_SET:
        if a in v.aliases or a == v.name: return -1
    for i in INSTRUCTION_SET:
        if a in i.aliases or a == i.name: return -1
    for v in VALUES_SET:
        if a == v.name: return -1
    VALUES_SET.append(ValueAlias(val, a))
    return 0

def checkValue(s):
    for v in VALUES_SET:
        if v.name == s: return True
    return False

def getValue(s):
    for v in VALUES_SET:
        if v.name == s: return str(v.val)
    return 0

def resetAliases():
    for i in INSTRUCTION_SET:
        i.aliases = []
    for v in VARIABLE_SET:
        v.aliases = []
    VALUES_SET = []
