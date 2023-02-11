from itertools import product

size = 10
horizon = 1

def neighbours(cell):
    for c in product(*(range(n-horizon, n+horizon+1) for n in cell)):
        if c != cell and all(0 <= n < size for n in c):
            yield c

print(list(neighbours((0,0))))