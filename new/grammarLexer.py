from enum import Enum

class TOKEN(Enum):
    ERROR = -2
    EOF = -1
    IDENT = 0
    KEYWORD = 1
    SYMBOL = 2
    TOKEN_NAME = 3
    TOKEN_ALIAS = 4
    ASTIN = 5

SYMBOLES_1 = ["|"]
SYMBOLES_2 = ["$$", ":="]
SYMBOLES_4 = ["$$$$"]
KEYWORDS = ["$token", "$base", "<empty>"]

class Token:
    def __init__(self, val: str, typ: TOKEN, line: int, col: int):
        self.val = val
        self.typ = typ
        self.line = line
        self.col = col
    def __str__(self) -> str:
        return self.typ.name + " " + self.val + " " + str(self.line) + ":" + str(self.col)
    def __repr__(self) -> str:
        return f"Token({self.val}, TOKEN.{self.typ.name}, {self.line}, {self.col})"
    def parseStr(self) -> str:
        out = "Term__" + self.typ.name
        if self.typ == TOKEN.KEYWORD:
            if self.val == "$token": 
                return "Term__KEYWORD_token"
            if self.val == "$base": 
                return "Term__KEYWORD_base"
            if self.val == "<empty>": 
                return "Term__KEYWORD_empty"
        if self.typ == TOKEN.SYMBOL:
            out += "_" + self.val
            if self.val == "$$$$":
                out = out[:-1]
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

def findTokenName(fileContent):
    tn, _ = fileContent.split(maxsplit=1)
    parts = tn.split('_')
    if len(parts) != 2:
        return False
    if not parts[0].isupper():
        return False
    # other checks ?
    return True
    
def tryLexAst(fileContent):
    astin = ""
    nbbrace = 1
    while True:
        if len(fileContent) < 1 or fileContent[0] == "\n":
            return None
        if fileContent[0] == "{":
            nbbrace += 1
        if fileContent[0] == "}":
            nbbrace -= 1
            if nbbrace == 0:
                return astin
        astin += fileContent[0]
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

    # TOKEN_NAME
    if findTokenName(fileContent):
        tn, _ = fileContent.split(maxsplit=1)
        return Token(tn, TOKEN.TOKEN_NAME, line, col), fileContent[len(tn):]

    # TOKEN_ALIAS
    if fileContent[0] == "'" and len(fileContent) > 2 and fileContent[2] == "'":
        return Token(fileContent[0:3], TOKEN.TOKEN_ALIAS, line, col), fileContent[3:]

    # ASTIN
    if fileContent[0] == "{":
        astin = tryLexAst(fileContent[1:])
        if astin is not None:
            return Token(astin, TOKEN.ASTIN, line, col), fileContent[len(astin)+2:]

    # KEYWORD
    if fileContent[0] == "$":
        ident = identifierLex(fileContent[1:])
        if "$" + ident in KEYWORDS:
            return Token("$"+ident, TOKEN.KEYWORD, line, col), fileContent[len(ident)+1:]
    if fileContent[0:7] == "<empty>":
        return Token("<empty>", TOKEN.KEYWORD, line, col), fileContent[7:]

    # id
    if fileContent[0].isalpha() or fileContent[0] == "_":
        ident = identifierLex(fileContent)
        return Token(ident, TOKEN.IDENT, line, col), fileContent[len(ident):]

    # symboles
    if fileContent[0:4] in SYMBOLES_4:
        return Token(fileContent[0:4], TOKEN.SYMBOL, line, col), fileContent[4:]
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

def main():
    txt = ""
    with open("grammarDef.txt") as f:
        txt = f.read()
    tokks = lexAll(txt)
    for t in tokks:
        print(t)


if __name__ == "__main__":
    main()
