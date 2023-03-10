import matplotlib.pyplot as plt
import numpy as np

# plot a line from (1, 3) to (8, 10), we have to pass two arrays [1, 8] and [3, 10] to the plot function.
xpoints = np.array([1, 8])
ypoints = np.array([3, 10])


# plot a line
plt.plot(xpoints, ypoints)
# plot points without line
# plt.plot(xpoints, ypoints, 'o')

plt.show()