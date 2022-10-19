#!/usr/bin/env python3

class PostFixOp:
    def __init__(self, symbole, p, opS, opf):
        self.symbole = symbole
        self.p = p
        self.stackOPS = opS
        self.stackOPf = opf

OP_PUSH_S = 102
OP_PUSH_F = 103

def checkSimpleOp(symboles, t, time, instructionCount):

    # test if it's a simple case
    if len(symboles) < 3: return -1, instructionCount
    var1 = symboles[0]
    ins = -1

    # Inc and Dec
    if symboles[1] == symboles[2] and (symboles[1] == '+' or symboles[1] == '-'):
        if len(symboles) > 3: return -1, instructionCount
        if   t == 'S' and symboles[1] == '+': ins = (106,time,[var1, '1'], instructionCount)
        elif t == 'S' and symboles[1] == '-': ins = (108,time,[var1, '1'], instructionCount)
        elif t == 'f' and symboles[1] == '+': ins = (107,time,[var1, '1.'], instructionCount)
        elif t == 'f' and symboles[1] == '-': ins = (109,time,[var1, '1.'], instructionCount)
        instructionCount += 16

    # affectExpr
    elif symboles[2] == '=':
        if len(symboles) != 4: return -1, instructionCount
        var2 = symboles[3]
        if   t == 'S' and symboles[1] == '+': ins = (106, time, [var1, var2], instructionCount)
        elif t == 'f' and symboles[1] == '+': ins = (107, time, [var1, var2], instructionCount)
        elif t == 'S' and symboles[1] == '-': ins = (108, time, [var1, var2], instructionCount)
        elif t == 'f' and symboles[1] == '-': ins = (109, time, [var1, var2], instructionCount)
        elif t == 'S' and symboles[1] == '*': ins = (110, time, [var1, var2], instructionCount)
        elif t == 'f' and symboles[1] == '*': ins = (111, time, [var1, var2], instructionCount)
        elif t == 'S' and symboles[1] == '/': ins = (112, time, [var1, var2], instructionCount)
        elif t == 'f' and symboles[1] == '/': ins = (113, time, [var1, var2], instructionCount)
        elif t == 'S' and symboles[1] == '%': ins = (114, time, [var1, var2], instructionCount)
        elif t == 'f' and symboles[1] == '%': ins = (115, time, [var1, var2], instructionCount)
        else: return -1, instructionCount
        instructionCount += 16

    # affect then expr
    elif symboles[1] == '=':
        if len(symboles) == 3:
            var2 = symboles[2]
            if   t == 'S': ins = (100, time, [var1, var2], instructionCount)
            elif t == 'f': ins = (101, time, [var1, var2], instructionCount)
            instructionCount += 16
        elif len(symboles) == 5:
            var2 = symboles[2]
            var3 = symboles[4]
            if   t == 'S' and symboles[3] == '+': ins = (116, time, [var1, var2, var3], instructionCount)
            elif t == 'f' and symboles[3] == '+': ins = (117, time, [var1, var2, var3], instructionCount)
            elif t == 'S' and symboles[3] == '-': ins = (118, time, [var1, var2, var3], instructionCount)
            elif t == 'f' and symboles[3] == '-': ins = (119, time, [var1, var2, var3], instructionCount)
            elif t == 'S' and symboles[3] == '*': ins = (120, time, [var1, var2, var3], instructionCount)
            elif t == 'f' and symboles[3] == '*': ins = (121, time, [var1, var2, var3], instructionCount)
            elif t == 'S' and symboles[3] == '/': ins = (122, time, [var1, var2, var3], instructionCount)
            elif t == 'f' and symboles[3] == '/': ins = (123, time, [var1, var2, var3], instructionCount)
            elif t == 'S' and symboles[3] == '%': ins = (124, time, [var1, var2, var3], instructionCount)
            elif t == 'f' and symboles[3] == '%': ins = (125, time, [var1, var2, var3], instructionCount)
            else: return -1, instructionCount
            instructionCount += 20
        else: return -1, instructionCount
    return ins, instructionCount

OPSYM = [
    PostFixOp("+", 4, 142, 143),
    PostFixOp("-", 4, 144, 145),
    PostFixOp("*", 5, 146, 147),
    PostFixOp("/", 5, 148, 149),
    PostFixOp("%", 5, 150, 151),
    PostFixOp("==", 3, 152, 153),
    PostFixOp("!=", 3, 154, 155),
    PostFixOp(">", 3, 156, 157),
    PostFixOp(">=", 3, 158, 159),
    PostFixOp("<", 3, 160, 161),
    PostFixOp("<=", 2, 162, 163),
    PostFixOp("&&", 1, 165, 165),
    PostFixOp("||", 1, 166, 166),
    PostFixOp("^", 1, 167, 167),
]


def checkOpSymbole(symboles):
    s= -1
    n = 0
    for o in OPSYM:
        if o.symbole == symboles[0]:
            s = o.symbole
            n = 1
    if len(symboles) > 1:
        for o in OPSYM:
            if o.symbole == symboles[0]+symboles[1]:
                s = o.symbole
                n = 2
    return s, n

def getOperator(sym):
    for o in OPSYM:
        if o.symbole == sym:
            return o
    return -1

def isNumber(n):
    return n.replace(".","").isnumeric()

def parenth(newsymboles, i = 0):
    ##print##(i*" ",newsymboles,sep='')
    if len(newsymboles) < 4:
        if len(newsymboles) == 1:
            if type(newsymboles[0]) == list: return parenth(newsymboles[0])
            else: return newsymboles[0]
        ##print##(i*" "+"casSimple:")
        stack = [0,0,0]
        if type(newsymboles[0]) == list: stack[0] = parenth(newsymboles[0],i+1)
        else: stack[0] = newsymboles[0]
        stack[1] = newsymboles[1]
        if type(newsymboles[2]) == list: stack[2] = parenth(newsymboles[2],i+1)
        else: stack[2] = newsymboles[2]
        ##print##(i*" "+"-> ", stack)
        return stack
    else:
        stack = [0,0,0]
        o1 = getOperator(newsymboles[1])
        o2 = getOperator(newsymboles[3])
        if o1.p < o2.p:
            ##print##(i*" "+"cas a(bc):")
            if type(newsymboles[0]) == list: stack[0] = parenth(newsymboles[0],i+1)
            else: stack[0] = newsymboles[0]
            stack[1] = newsymboles[1]
            stack[2] = parenth(newsymboles[2:],i+1)
        else:
            ##print##(i*" "+"cas (ab)c:")
            stack[0] = parenth(newsymboles[0:3],i+1)
            stack[1] = newsymboles[3]
            stack[2] = parenth(newsymboles[4:],i+1)
        ##print##(i*" "+"-> ", stack)
        return stack

def postFixStep(s):
    if type(s) != list:
        return [s]
    else:
        stack = [s[1]]
        stack = postFixStep(s[0]) + stack
        stack = postFixStep(s[2]) + stack
        return stack


def postFix(newsymboles):
    return postFixStep(parenth(newsymboles))

def parseExpression(symboles):
    newsymboles = []
    predList = []
    while len(symboles) > 0:
        if symboles[0] == '(':
            predList.append(newsymboles.copy())
            newsymboles = []
            symboles = symboles[1:]
            continue
        elif symboles[0] == ')':
            lc = newsymboles.copy()
            newsymboles = predList.pop()
            newsymboles.append(lc)
            symboles = symboles[1:]
            continue
        o, n = checkOpSymbole(symboles)
        if o == -1:
            newsymboles.append(symboles[0])
            symboles = symboles[1:]
        else:
            newsymboles.append(o)
            symboles = symboles[n:]
    a = []
    return postFix(newsymboles)

def getInsExpr(symboles, t, time, insCnt):
    postfix = parseExpression(symboles)
    ins = []
    for s in postfix:
        o = getOperator(s)
        if o != -1:
            ins.append(((o.stackOPf,o.stackOPS)[t=="S"], time, [], insCnt))
            insCnt += 8
        else:
            ins.append(((OP_PUSH_F,OP_PUSH_S)[t=="S"], time, [s], insCnt))
            insCnt += 12
    return ins, insCnt

def tryPostFix(pf):
    st = []
    for s in pf:
        if isNumber(s):
           st.append(float(s))
           ##print##("push", s)
        else:
            if s == "+":
                a = st.pop()
                b = st.pop()
                st.append(a+b)
                ##print##("pop", a)
                ##print##("pop", b)
                ##print##("push", a+b)
            elif s == "-":
                a = st.pop()
                b = st.pop()
                st.append(a-b)
                ##print##("pop", a)
                ##print##("pop", b)
                ##print##("push", a-b)
            elif s == "*":
                a = st.pop()
                b = st.pop()
                st.append(a*b)
                ##print##("pop", a)
                ##print##("pop", b)
                ##print##("push", a*b)
            elif s == "/":
                a = st.pop()
                b = st.pop()
                st.append(a/b)
                ##print##("pop", a)
                ##print##("pop", b)
                ##print##("push", a/b)
            elif s == "%":
                a = st.pop()
                b = st.pop()
                st.append(a%b)
                ##print##("pop", a)
                ##print##("pop", b)
                ##print##("push", a%b)

    return st.pop()
