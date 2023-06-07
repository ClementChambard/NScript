from .grammar.grammarRule import GrammarRule  # noqa F401


logLevel = 0


def readDotGram(filename):
    text = ""
    with open(filename, "r") as f:
        text = f.read()
    return eval(text)


def parse(rules, stateTable, lexfunc, text):
    tokens = [[t.parseStr(), t] for t in lexfunc(text)]

    stack = [0]
    symbolStack = []

    while True:
        action = stateTable[stack[-1]].get(
            tokens[0][0], stateTable[stack[-1]]["DEFAULT"]
        )

        if action[0] == "Err":
            print("Error: unexpected", tokens[0][0], "in state", stack)
            [print(s) for s in stateTable]
            return

        if action[0] == "S":
            if logLevel > 0:
                print("Shift", tokens[0][0])
            symbolStack.append(tokens[0][1])
            tokens = tokens[1:]
            stack.append(action[1])

        if action[0] == "R":
            reduceRule = rules[action[1]]
            if logLevel > 0:
                print("Reduce", reduceRule)
            toReduce = []
            if reduceRule.size > 0:
                toReduce = symbolStack[-reduceRule.size :]
                symbolStack = symbolStack[: -reduceRule.size]
                stack = stack[: -reduceRule.size]
            symbolStack.append(reduceRule.ast(toReduce))
            action = stateTable[stack[-1]].get(
                reduceRule.out, stateTable[stack[-1]]["DEFAULT"]
            )
            if action[0] != "S":
                print("ERROR")
                return
            stack.append(action[1])

        if action[0] == "OK":
            if logLevel > 0:
                print("OK")
            return symbolStack[0]
