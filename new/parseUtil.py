from lexer import Token, TOKEN

contexts = []

def useContext(func):
    def wrapper(*args, autoskip = True, tokens = [], **kwargs):
        pushContext(tokens)
        val = func(*args, **kwargs)
        skip = popContext(autoskip = autoskip)
        if not autoskip: return val, skip
        return val
    return wrapper

def needsContext(default = []):
    def inner(func):
        def wrapper(*args, **kwargs):
            if len(contexts) < 1: return default
            return func(*args, **kwargs)
        return wrapper
    return inner

def pushContext(tokens: []):
    if len(tokens) == 0 and len(contexts) > 0: contexts.append([Next(), 0])   
    else: contexts.append([tokens, 0])   

@needsContext(default = ())
def Skip(count: int = 1) -> ():
    contexts[-1][1] += count

@needsContext(default = False)
def Check(typ, val = "", skip = False) -> bool:
    tok = Tok(skip)
    return tok.typ == typ and (val == "" or tok.val == val)

def CheckSkip(typ, val = "") -> bool:
    a = Check(typ, val, skip = True)
    return a

def CheckOpt(typ, val = "") -> bool:
    ret = Check(typ, val)
    if ret: Skip()
    return ret

@needsContext(default = 0)
def popContext(autoskip = True) -> int:
    skip = contexts[-1][1]
    contexts.pop()
    if autoskip: Skip(skip)
    return skip

@needsContext(default = [])
def Tok(skip = True) -> Token:
    if len(contexts[-1][0]) < 1: return Token("", TOKEN.ERROR, -1, -1)
    tok = contexts[-1][0][contexts[-1][1]]
    if skip: Skip()
    return tok

@needsContext(default = [])
def Last() -> Token:
    if len(contexts[-1][0]) < 1 or contexts[-1][1] < 1: return Token("", TOKEN.ERROR, -1, -1)
    return contexts[-1][0][contexts[-1][1]-1]

@needsContext(default = [])
def Next() -> [Token]:
    return contexts[-1][0][contexts[-1][1]:]

@needsContext(default = [])
def Seen() -> [Token]:
    return contexts[-1][0][:contexts[-1][1]]

@needsContext(default = [])
def All() -> [Token]:
    return contexts[-1][0]

def LoopParse(func, endType, endSymb = ""):
    pass

