from itertools import product, starmap
x, y = (5, 5)
cells = list(starmap(lambda a, b: (x + a, y + b), product((0, -1, +1), (0, -1, +1))))
print(cells - [(5,5)])

# from itertools import starmap
 
# li =[(2, 5), (3, 2), (4, 3)]
 
# new_li = list(starmap(pow, li))
 
# print(new_li)