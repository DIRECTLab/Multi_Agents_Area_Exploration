import numpy as np
import matplotlib.pyplot as plt

x = np.array([80, 85, 90, 95, 100, 105, 110, 115, 120, 125])
y = np.array([240, 250, 260, 270, 280, 290, 300, 310, 320, 330])

plt.plot(x, y)

# use the xlabel() and ylabel() functions to set a label for the x- and y-axis
# use the title() function to set a title for the plot
plt.title("Sports Watch Data")
plt.xlabel("Average Pulse")
plt.ylabel("Calorie Burnage")

# use the fontdict parameter in xlabel(), ylabel(), and title() to set font properties for the title and labels
# font1 = {'family':'serif','color':'blue','size':20}
# plt.title("Sports Watch Data", fontdict=font1)

# use the loc parameter to position the title and the labels
# Legal values are: 'left', 'right', and 'center'. Default value is 'center'.

plt.show()