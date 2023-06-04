import lexer
import grammar.readGrammar as rg
from grammar.grammarRule import GrammarRule

rules, stateTable = rg.readfile("grammarDef.txt")
logLevel = 0

def parse(tokens: [list]):
    stack = [0]
    symbolStack = []

    while True:
        action = stateTable[stack[-1]].get(tokens[0][0], stateTable[stack[-1]]["DEFAULT"])

        if action[0] == "Err":
            print("Error: unexpected", tokens[0][0], "in state", stack)
            [print(s) for s in stateTable]
            return

        if action[0] == "S":
            if logLevel > 0: print("Shift", tokens[0][0])
            symbolStack.append(tokens[0][1])
            tokens = tokens[1:]
            stack.append(action[1])

        if action[0] == "R":
            reduceRule = rules[action[1]]
            if logLevel > 0: print("Reduce", reduceRule)
            toReduce = []
            if reduceRule.size > 0:
                toReduce = symbolStack[-reduceRule.size:]
                symbolStack = symbolStack[:-reduceRule.size]
                stack = stack[:-reduceRule.size]
            symbolStack.append(reduceRule.ast(toReduce))
            action = stateTable[stack[-1]].get(reduceRule.out, stateTable[stack[-1]]["DEFAULT"])
            if action[0] != "S":
                print("ERROR")
                return
            stack.append(action[1])

        if action[0] == "OK":
            if logLevel > 0: print("OK")
            return symbolStack[0]

if __name__ == "__main__":
    print(parse([[t.parseStr(),t] for t in lexer.lexAll("""
    type t @ test {
       int8 fieldi = (83+(123 + 3));
       string fields @ alias = ("123"+"123");
       float fieldf = 0.;
    }
    """)]))
            
            

