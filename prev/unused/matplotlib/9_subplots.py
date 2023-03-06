import matplotlib.pyplot as plt
import numpy as np

# With the subplot() function you can draw multiple plots in one figure
# The subplot() function takes three arguments that describes the layout of the figure.
# The layout is organized in rows and columns, which are represented by the first and second argument.
# The third argument represents the index of the current plot.

#plot 1:
x = np.array([0, 1, 2, 3])
y = np.array([3, 8, 1, 10])
plt.subplot(1, 2, 1)
#the figure has 1 row, 2 columns: this plot is the first plot. 
plt.plot(x,y)

#plot 2:
x = np.array([0, 1, 2, 3])
y = np.array([10, 20, 30, 40])
plt.subplot(1, 2, 2)
#the figure has 1 row, 2 columns: this plot is the second plot. 
plt.plot(x,y)

# Draw 2 plots on top of each other
# Rather than saying the total plot has 1 row and 2 column, say total plot will have 2 row and 1 column.
# plt.subplot(2, 1, ...)

plt.show()