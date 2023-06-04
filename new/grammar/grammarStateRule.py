from .grammarRule import GrammarRule

class GrammarStateRule:
    def __init__(self, rule: GrammarRule, pos: int):
        self.rule = rule
        self.pos = pos

    def __str__(self) -> str:
        out = f"{self.rule.out} := "
        if "<empty>" in self.rule.tokens: return out + "."
        for i, t in enumerate(self.rule.tokens):
            if i == self.pos:
                out += "."
            out += t + " "
        if i >= len(self.rule.tokens): out += "."
        return out

    def __eq__(self, o):
        if self.pos != o.pos: return False
        if self.rule != o.rule: return False
        return True

    def __hash__(self):
        return (self.rule.__hash__() + (self.pos * 109263891))

    def others(self, rules: [GrammarRule]):
        if self.pos >= len(self.rule.tokens): return []
        tok = self.rule.tokens[self.pos]
        if not "NTerm__" in tok: return []
        o = set()
        for r in rules:
            if r.out == tok:
                new = GrammarStateRule(r, 0)
                oldlen = len(o)
                o.add(new)
                newlen = len(o)
                if newlen > oldlen: o.update(new.others(rules))
        return list(o)

    def advance(self):
        if self.pos >= len(self.rule.tokens): return -1, -1
        return self.rule.tokens[self.pos], GrammarStateRule(self.rule, self.pos+1)

    def completeState(state: [], rules: [GrammarRule]):
        out = set(state)
        for s in state:
            out.update(s.others(rules))
        return list(out)
