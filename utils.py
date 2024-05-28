import random


def randomInt(b: int, e: int):
    return random.randint(b, e)


def getVariableOrDefault(varName: str, defaultValue):
    if varName in vars():
        return eval(varName)
    else:
        return defaultValue
