
class GrammarRule:
    def __init__(self, tokens: [str], size: int, out: str, astFunc):
        self.tokens = tokens
        self.size = size
        self.out = out
        self.ast = astFunc
        self.i = 0

    def empty(self) -> bool:
        return self.size == 0

    def __hash__(self):
        return (" ".join(self.tokens)+" " +str(self.size) + self.out).__hash__()

    def __eq__(self, o):
        if len(o.tokens) != len(self.tokens): return False
        for t1, t2 in zip(self.tokens, o.tokens): 
            if t1 != t2: return False
        if self.size != o.size: return False
        if self.out != o.out: return False
        return True

    def __str__(self) -> str:
        o = f"{self.out} := "
        for t in self.tokens:
            o += t + " "
        return o.strip()

    def __repr__(self) -> str:
        o = "GrammarRule(["
        for t in self.tokens:
            o+=t + ","
        o += f"], {self.size}, {self.out}, {self.ast})"
        return o
