from itertools import product

size = [5, 10]
horizon = 3

def neigh(cell):
    for c in product(*(range(n-horizon, n+horizon+1) for n in cell)):
        # if c != cell and all(0 <= n < size for n in c):
            # yield c
        if (c != cell and all(0 <= i < bound for i, bound in zip(c, size))):
            yield c


print(list(neigh((2,2))))