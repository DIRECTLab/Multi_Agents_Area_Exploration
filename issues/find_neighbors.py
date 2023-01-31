MX = 10
MY = 10


def neighbours(x, y):
    pn = [(x-1, y), (x+1, y), (x-1, y-1), (x, y-1),
          (x+1, y-1), (x-1, y+1), (x, y+1), (x+1, y+1)]
    for i, t in enumerate(pn):
        if t[0] < 0 or t[1] < 0 or t[0] >= MX or t[1] >= MY:
            pn[i] = None
    return [c for c in pn if c is not None]


print(neighbours(0,0))
