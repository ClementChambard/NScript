class sym:
    def __init__(self, nt, v):
        self.nt = nt
        self.v = v

    def isTerminal(self):
        return not self.nt

    def __eq__(self, other):
        return self.nt == other.nt and self.v == other.v

    def __str__(self):
        return str(self.v)

    def __repr__(self):
        return ["T('", "NT('"][self.nt] + self.v + "')"

    def __hash__(self):
        sign = (1, -1)[self.nt]
        return self.v.__hash__() * sign

class rule:
    def __init__(self, p, s):
        self.p = p
        self.symboles = s

    def produces(self, nterm):
        return self.p == nterm

    def isNone(self):
        return len(self.symboles) == 0

def memo(f):
    data = {}
    def wrapper(*args):
        if args[0] in data.keys():
            return data[args[0]]
        ret = f(*args)
        data[args[0]] = ret
        return ret
    return wrapper

@memo
def first(sym, rules, ignore):

  def firstChain(symboles, rules, ignore):
    fsts = first(symboles[0], rules, ignore)
    if None in fsts and len(symboles) > 1:
      fsts.update(firstChain(symboles[1:], rules, ignore))
    return fsts

  if sym in ignore:
    return set()
  if sym.isTerminal():
    return set([sym])
  ignore.add(sym)
  out = set()
  for r in rules:
    if r.produces(sym):
      if r.isNone():
        out.add(None)
      else:
        out.update(firstChain(r.symboles, rules, ignore))
  return out

s_S = sym(True, "S")
s_A = sym(True, "A")
s_B = sym(True, "B")
s_C = sym(True, "C")
s_a = sym(False, "a")
s_b = sym(False, "b")
s_d = sym(False, "d")
s_g = sym(False, "g")
s_h = sym(False, "h")

r_S1 = rule(s_S, [s_A, s_C, s_B])
r_S2 = rule(s_S, [s_C, s_b, s_b])
r_S3 = rule(s_S, [s_B, s_a])
r_A1 = rule(s_A, [s_d, s_a])
r_A2 = rule(s_A, [s_B, s_C])
r_B1 = rule(s_B, [s_g])
r_B2 = rule(s_B, [])
r_C1 = rule(s_C, [s_h])
r_C2 = rule(s_C, [])

rules = [r_S1,r_S2,r_S3, r_A1, r_A2, r_B1, r_B2, r_C1, r_C2]

print(first(s_S, rules, set()))
