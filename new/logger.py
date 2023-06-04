import fileData as file
from lexer import Token

class COL:
    RESET     = '\033[0m'
    BOLD      = '\033[1m'
    FAINT     = '\033[2m'
    ITALIC    = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINKSLOW = '\033[5m'
    BLINKFAST = '\033[6m'
    INVERT    = '\033[7m'
    INVISIBLE = '\033[8m'
    STROKE    = '\033[9m'
    NOBOLD    = '\033[22m'
    NOITALIC  = '\033[23m'
    NOUNDERLI = '\033[24m'
    NOBLINK   = '\033[25m'
    NOINVERT  = '\033[27m'
    NOINVISI  = '\033[28m'
    NOSTROKE  = '\033[29m'
    FG_BLACK  = '\033[30m'
    FG_RED    = '\033[31m'
    FG_GREEN  = '\033[32m'
    FG_YELLOW = '\033[33m'
    FG_BLUE   = '\033[34m'
    FG_PURPLE = '\033[35m'
    FG_CYAN   = '\033[36m'
    FG_WHITE  = '\033[37m'
    FG_RESET  = '\033[39m'
    BLACK     = '\033[90m'
    RED       = '\033[91m'
    GREEN     = '\033[92m'
    YELLOW    = '\033[93m'
    BLUE      = '\033[94m'
    PURPLE    = '\033[95m'
    CYAN      = '\033[96m'
    WHITE     = '\033[97m'
    def setFG(r, g, b):
        return '\033[38;2;' + str(r) + ';' + str(g) + ';' + str(b) + 'm'
    def setFG(n):
        return '\033[38;5;' + str(n) + 'm'

def error(token: Token, err: str):
    file.errors += 1
    lineNumStr = file.name + ":" + str(token.line) + ":" + str(token.col) + ": "
    line = " " * 30
    if token.line < len(file.lines):
        line = file.lines[token.line]
    lineStr = line[:token.col] + COL.RED + token.val + COL.RESET + line[token.col+len(token.val):]
    underlineStr = " " * token.col + COL.RED + "^" + "~" * max(0, len(token.val)-1) + COL.RESET
    print(COL.RED + "error:" + COL.RESET, err)
    print(lineNumStr + lineStr)
    print(" " * len(lineNumStr) + underlineStr)

def note(token: Token, err: str):
    filename = "test"
    lineNumStr = file.name + ":" + str(token.line) + ":" + str(token.col) + ": "
    line = file.lines[token[2]]
    lineStr = line[:token.col] + COL.CYAN + token.val + COL.RESET + line[token.col+len(token.val):]
    underlineStr = " " * token.col + COL.CYAN + "^" + "~" * max(0, len(token.val)-1) + COL.RESET
    print(COL.CYAN + "note:" + COL.RESET, err)
    print(lineNumStr + lineStr)
    print(" " * len(lineNumStr) + underlineStr)
