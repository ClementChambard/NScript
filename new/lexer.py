from enum import Enum

class TOKEN(Enum):
    ERROR = -2
    EOF = -1
    IDENT = 0
    KEYWORD = 1
    INT = 2
    FLOAT = 3
    STR = 4
    SYMBOL = 5

OPERATORS_1 = ["+", "-", "<", ">", "/", "*", "%", "!", "&", "|"]
SYMBOLES_1 = ["@", ";", "{", "}", "=", ".", "(", ")"] + OPERATORS_1
SYMBOLES_2 = ["<=", ">=", "==", "!=", "&&", "||"]
KEYWORDS = ["type"]

class Token:
    def __init__(self, val: str, typ: TOKEN, line: int, col: int):
        self.val = val
        self.typ = typ
        self.line = line
        self.col = col
    def __str__(self) -> str:
        return self.typ.name + " " + self.val + " " + self.line + ":" + self.col
    def __repr__(self) -> str:
        return f"Token({self.val}, TOKEN.{self.typ.name}, {self.line}, {self.col})"
    def parseStr(self) -> str:
        out = "Term__" + self.typ.name
        if self.typ == TOKEN.KEYWORD or self.typ == TOKEN.SYMBOL:
            out += "_" + self.val
        return out


def errorLex(fileContent: str, read: str) -> (str, int):
    tok = read
    while fileContent != "" and fileContent[0].isalnum():
        tok += fileContent[0]
        fileContent = fileContent[1:]
    return tok, TOKEN.ERROR

def identifierLex(fileContent: str) -> str:
    ident = fileContent[0]
    fileContent = fileContent[1:]
    while fileContent != "" and (fileContent[0].isalnum() or fileContent[0] == "_"):
        ident += fileContent[0]
        fileContent = fileContent[1:]
    return ident

def numberLex(fileContent: str) -> (str, TOKEN):
    isFloat = False
    isHex = False
    isBinary = False
    nb = ""
    while fileContent != "":
        nb += fileContent[0]
        fileContent = fileContent[1:]
        if fileContent[0] == ".":
            if isFloat or isHex or isBinary: return errorLex(fileContent, nb)
            else: isFloat = True
        elif fileContent[0] == "x" and nb == "0":
            isHex = True
        elif fileContent[0] == "b" and nb == "0":
            isBinary = True
        elif fileContent[0].isalpha():
            if fileContent[0] in "ABCDEFabcdef":
                if not isHex: return errorLex(fileContent, nb)
            else: return errorLex(fileContent, nb)
        elif fileContent[0].isdecimal():
            if fileContent[0] in "23456789" and isBinary: return errorLex(fileContent, nb)
            if fileContent[0] in "89" and len(nb) > 0 and nb[0] == "0": return errorLex(fileContent, nb)
        elif nb == ".":
            return ".", TOKEN.SYMBOL
        else:
            break

    return nb, (TOKEN.INT, TOKEN.FLOAT)[isFloat]
    
def lineComment(fileContent: str, line: int, col: int) -> (Token, str):
    if fileContent[0] == "\n":
        return lex(fileContent[1:], line+1, 0)
    return lineComment(fileContent[1:], line, col+1)

def multilineComment(fileContent: str, line: int, col: int) -> (Token, str):
    if fileContent[0] == "\n":
        return multilineComment(fileContent[1:], line+1, 0)
    if fileContent[0:2] == "*/":
        return lex(fileContent[2:], line, col+2)
    return multilineComment(fileContent[1:], line, col+1)

def string(fileContent: str) -> (str, int):
    s = ""
    backslash = False
    while True:
        if fileContent[0] == "\n": # no linebreak
            return s, -1
        elif fileContent[0] == "\\":
            if backslash: 
                s += "\\"
                backslash = False
            else: backslash = True
        elif fileContent[0] == "\"":
            if backslash:
                s += "\""
                backslash = False
            else: return s, 0
        else:
            if backslash:
                s += "\\"
                backslash = False
            s += fileContent[0]
        fileContent = fileContent[1:]

def lex(fileContent: str, line: int, col: int) -> (Token, str):
    
    # EOF
    if fileContent == "":
        return Token("", TOKEN.EOF, line, col), fileContent

    # white spaces
    if fileContent[0] == " ":
        return lex(fileContent[1:], line, col+1)
    if fileContent[0] == "\n":
        return lex(fileContent[1:], line+1, 0)

    # comments
    if fileContent[0:2] == "//":
        return lineComment(fileContent[2:], line, col + 2)
    if fileContent[0:2] == "/*":
        return multilineComment(fileContent[2:], line, col + 2)

    # string litteral
    if fileContent[0] == "\"":
        s, status = string(fileContent[1:])
        if status == -1: 
            return Token("\"" + s, TOKEN.ERROR, line, col), fileContent[len(s)+1:]
        return Token("\""+s+"\"", TOKEN.STR, line, col), fileContent[len(s)+2:]

    # id/keyword
    if fileContent[0].isalpha() or fileContent[0] == "_":
        ident = identifierLex(fileContent)
        if ident in KEYWORDS:
            return Token(ident, TOKEN.KEYWORD, line, col), fileContent[len(ident):]
        return Token(ident, TOKEN.IDENT, line, col), fileContent[len(ident):]

    # number
    if fileContent[0].isdecimal() or fileContent[0] == ".":
        nb, typ = numberLex(fileContent)
        return Token(nb, typ, line, col), fileContent[len(nb):]

    # symboles
    if fileContent[0:2] in SYMBOLES_2:
        return Token(fileContent[0:2], TOKEN.SYMBOL, line, col), fileContent[2:]
    if fileContent[0] in SYMBOLES_1:
        return Token(fileContent[0], TOKEN.SYMBOL, line, col), fileContent[1:]

    # error 
    return Token(fileContent[0], TOKEN.ERROR, line, col), fileContent[1:]
    
def lexAll(fileContent: str):
    col = 0
    line = 0
    tokens = []
    while True:
        tok, fileContent = lex(fileContent, line, col)
        col = tok.col + len(tok.val)
        line = tok.line
        tokens.append(tok)
        if tok.typ == TOKEN.EOF: 
            break
    return tokens

