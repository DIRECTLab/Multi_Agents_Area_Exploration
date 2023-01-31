import matplotlib.pyplot as plt
import numpy as np

# If we do not specify the points in the x-axis, 
# they will get the default values 0, 1, 2, 3, (etc. depending on the length of the y-points.
ypoints = np.array([3, 8, 1, 10, 5, 7])

plt.plot(ypoints)
plt.show()