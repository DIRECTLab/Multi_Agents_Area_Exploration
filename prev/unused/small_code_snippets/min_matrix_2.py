import numpy as np

A = np.array([0,1,2])
B = np.array([1,0,3])
C = np.array([3,0,4])
D = np.array([7,0,4])
print(np.minimum.reduce([A,B,C,D]))