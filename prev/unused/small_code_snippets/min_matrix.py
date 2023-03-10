# Linear Algebra Learning Sequence
# Minimum Value Comparing

import numpy as np

matrix_A = np.array([
    [0.0,1.0,2.0,3.0,4.0,5.0],
    [1.0,1.41,2.23,3.16,4.12,5.09],
    [2.0,2.23,2.82,3.60,4.47,5.38],
    [3.0,3.16,3.60,4.24,5.0,5.83],
    [4.0,4.12,4.47,5,5.65,6.4],
    [5.0,5.09,5.38,5.83,6.40,7.07]
])

matrix_B = np.array([
    [2.23,1.41,1.0,1.41,2.23,3.16],
    [2.0,1.0,0.0,1.0,2.0,3.0],
    [2.23,1.41,1.0,1.41,2.23,3.16],
    [2.82,2.23,2.0,2.23,2.82,3.60],
    [3.60,3.16,3.0,3.16,3.60,4.24],
    [4.47,4.12,4.0,4.12,4.47,5]
])

matrix_C = np.array([
    [2.23,1.41,1.0,1.41,2.23,3.16],
    [2.0,1.0,0.0,1.0,2.0,3.0],
    [2.23,1.41,1.0,1.41,2.23,3.16],
    [2.82,2.23,2.0,2.23,2.82,3.60],
    [3.60,3.16,3.0,3.16,3.60,4.24],
    [4.47,4.12,4.0,4.12,4.47,3]
])

# print("\n\n---Matrix A---\n", matrix_A)
# print("\n\n---Matrix B---\n", matrix_B)
# print('\n\n---minimum value comparasion : \n', np.minimum(matrix_A,matrix_B))
print('\n\n---minimum value comparasion : \n', np.minimum.reduce([matrix_A,matrix_B,matrix_C]))
# print(np.minimum.reduce([A,B,C,D]))




