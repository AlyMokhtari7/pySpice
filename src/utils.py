import random


def randomInt(lower_bound: int, upper_bound: int):
    return random.randint(lower_bound, upper_bound)

def randomFloat(lower_bound: int, upper_bound: int):
    return random.uniform(lower_bound, upper_bound)

def getVariableOrDefault(varName: str, defaultValue):
    if varName in vars():
        return eval(varName)
    else:
        return defaultValue
