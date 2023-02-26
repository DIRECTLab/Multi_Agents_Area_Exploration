import numpy as np
import matplotlib.pyplot as plt

# Define the data for the pet plot
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.tan(x)
y4 = np.exp(-x)

# Create the figure and the axes
fig = plt.figure(figsize=(8, 6))

# Define the grid for the subplots
ax1 = plt.subplot2grid((3, 2), (0, 0), rowspan=3, colspan=1)
rows = 3

for i in range(rows):
    ax = plt.subplot2grid((rows, 2), (i, 1), rowspan=1)
    ax.plot(x, y1)
    ax.set_xlim(0, 10)
    ax.set_xlabel('x')
    ax.set_ylabel('sin(x)')
# ax2 = plt.subplot2grid((3, 2), (0, 1), rowspan=1)
# ax3 = plt.subplot2grid((3, 2), (1, 1), rowspan=1)
# ax4 = plt.subplot2grid((3, 2), (2, 1), rowspan=1)


# Create the pet plot
ax1.plot(x, y1)
# ax2.plot(x, y2)
# ax3.plot(x, y3)
# ax3.plot(x, y4)



# Set the title for the pet plot
fig.suptitle('Pet Plot')

# Adjust the spacing between the subplots
fig.tight_layout()

# Show the pet plot
plt.show()
