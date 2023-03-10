import numpy as np
x_size, y_size = 3, 3
x_arr, y_arr = np.mgrid[0:x_size, 0:y_size]
cell = (0, 0)
dists = np.sqrt((x_arr - cell[0])**2 + (y_arr - cell[1])**2)
print(dists)
