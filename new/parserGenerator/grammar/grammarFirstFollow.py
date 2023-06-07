from .grammarRule import GrammarRule
from .grammarToken import GrammarToken

def memoNonTerm(func):
    mem = {}
    def wrapper(*args, **kwargs):
        if args[0] in mem.keys():
            return mem[args[0]]
        res = func(*args, **kwargs)
        mem[args[0]] = res
        return res
    return wrapper

@memoNonTerm
def firsts(nonTerm: str, rules: list[GrammarRule], tokens: list[GrammarToken], ignore = set()):
    ignore.update([nonTerm])
    out = set()
    for r in rules:
        if r.out != nonTerm: continue
        firstSymbole = r.tokens[0]
        if firstSymbole in [t.tok for t in tokens]:
            out.update([firstSymbole])
        elif firstSymbole not in ignore:
            out.update(firsts(firstSymbole, rules, tokens, ignore))
    return list(out) 

@memoNonTerm
def follows(nonTerm: str, rules: list[GrammarRule], tokens: list[GrammarToken], ignore = set()):
    ignore.update([nonTerm])
    out = set()
    for r in rules:
        positions = []
        for i, t in enumerate(r.tokens):
            if t == nonTerm: positions.append(i)
        if len(positions) == 0: continue
        for p in positions:
            if p >= len(r.tokens) - 1:
                if r.out not in ignore:
                    out.update(follows(r.out, rules, tokens, ignore))
            else:
                next = r.tokens[p+1]
                if next in [t.tok for t in tokens]:
                    out.update([next])
                else:
                    out.update(firsts(next, rules, tokens))
    return list(out)
