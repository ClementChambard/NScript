from typing import Any, Callable, Iterator, List, Optional, Self, Tuple

RecogRet = Tuple[bool, int, Optional[Any]]
RecogFunc = Callable[[str], RecogRet]


def match_ident(text: str) -> RecogRet:
    if not text[0].isalpha() and text[0] != "_":
        return False, 0, None
    i = 0
    while text[i].isalnum() or text[i] == "_":
        i += 1

    return True, i, f"IDENT({text[:i]})"


def match_keyword(kw: str) -> RecogFunc:
    def fn(text: str) -> RecogRet:
        ok, n, _ = match_ident(text)
        if not ok or n != len(kw):
            return False, 0, None
        if text[:n] == kw:
            return True, n, f"KEYWORD_{kw}"
        return False, 0, None

    return fn


def match_num(text: str) -> RecogRet:
    i = 0
    while text[i].isnumeric():
        i += 1
    if i == 0 or text[i].isalpha() or text[i] == "_":
        return False, 0, None
    return True, i, f"INTEGER({int(text[:i])})"


def match_symbole(sym: str) -> RecogFunc:
    def fn(text: str) -> RecogRet:
        if text[: len(sym)] == sym:
            return True, len(sym), f"SYMBOLE_{sym}"
        return False, 0, None

    return fn


LexedToken = Tuple[Any, int, int]


class LexerToken:
    def __init__(self: Self, recog_func: RecogFunc, priority: int):
        self.recog_func: RecogFunc = recog_func
        self.priority: int = priority

    def recognise(self: Self, text: str) -> RecogRet:
        return self.recog_func(text)


class Lexer:
    def __init__(self: Self, text: Optional[str] = None):
        self.pos: int = 0
        self.line: int = 0
        self.col: int = 0
        self.tokens: List[LexerToken] = []
        if text is not None:
            self.text: str = text

    def set_text(self: Self, text: str):
        self.pos = 0
        self.line = 0
        self.col = 0
        self.text = text

    def auto_add_symboles(
        self: Self, symb: List[List[str]], first_priority: int = 0
    ) -> int:
        i = first_priority
        for sl in symb:
            for s in sl:
                self.add_token(LexerToken(match_symbole(s), i))
            i += 1
        return i

    def auto_add_keywords(self: Self, kw: List[str], priority: int = 0):
        for k in kw:
            self.add_token(LexerToken(match_keyword(k), priority))

    def add_token(self: Self, tok: LexerToken):
        i: int = 0
        for t in self.tokens:
            if t.priority > tok.priority:
                break
            i += 1
        self.tokens.insert(i, tok)

    def print_check(self: Self):
        for t in self.tokens:
            print(t.priority)

    def eof(self: Self) -> bool:
        return self.pos >= len(self.text)

    def next_char(self: Self) -> str:
        return self.text[self.pos]

    def consume_char(self: Self) -> str:
        c = self.next_char()
        self.pos += 1
        return c

    def lex(self: Self) -> Iterator[LexedToken]:
        while not self.eof():
            if self.next_char() == "\n":
                self.consume_char()
                self.line += 1
                self.col = 0
                continue
            if self.next_char().isspace():
                self.consume_char()
                self.col += 1
                continue
            for t in self.tokens:
                ok, n, r = t.recognise(self.text[self.pos :])
                if ok:
                    yield r, self.line, self.col
                    self.pos += n
                    self.col += n
                    break
        yield "EOF", self.line, self.col
