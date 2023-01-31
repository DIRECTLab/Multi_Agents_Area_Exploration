import numpy as np

# CREATE AN EMPTY (zeros) list of lists:
MAP = np.zeros((6, 6), dtype=int)

print(MAP)
print(MAP.shape)
print(MAP.shape[0])  # ROWS
print(MAP.shape[1])  # COLUMNS

# [[0 0 0 0 0 0]
#  [0 0 0 0 0 0]
#  [0 0 0 0 0 0]
#  [0 0 0 0 0 0]
#  [0 0 0 0 0 0]
#  [0 0 0 0 0 0]]
# (6, 6)
# 6
# 6

# CREATE A RANDOMLY POPULATED LIST OF LISTS
cellMAP = np.random.randint(2, size=(6, 6))
print(cellMAP)

# [[1 0 0 1 0 0]
#  [1 1 0 1 0 1]
#  [1 1 1 0 0 0]
#  [1 0 0 1 0 0]
#  [1 1 1 1 1 0]
#  [0 0 1 1 1 0]]

# ITERATE OVER EACH ROW/COLUMN VALUE
for row in range(cellMAP.shape[0]):
    for column in range(cellMAP.shape[1]):
        print(cellMAP[row][column])

# 1
# 0
# 0
# 1
# 0
# 0
# 1
# 1
# 0... etc