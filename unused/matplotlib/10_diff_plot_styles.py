import matplotlib.pyplot as plt
import numpy as np

# SCATTER PLOT
# The scatter() function plots one dot for each observation. It needs two arrays of the same length, one for the values of the x-axis, and one for values on the y-axis
# x = np.array([5,7,8,7,2,17,2,9,4,11,12,9,6])
# y = np.array([99,86,87,88,111,86,103,87,94,78,77,85,86])
# plt.scatter(x, y)

# BAR PLOT
# With Pyplot, you can use the bar() function to draw bar graphs
# The bar() function takes arguments that describes the layout of the bars.
# The categories and their values represented by the first and second argument as arrays.
# x = np.array(["A", "B", "C", "D"])
# y = np.array([3, 8, 1, 10])
# plt.bar(x,y)

# HISTOGRAM
# A histogram is a graph showing frequency distributions.
# It is a graph showing the number of observations within each given interval.
# Example: Say you ask for the height of 250 people, you might end up with a histogram like this:
# In Matplotlib, we use the hist() function to create histograms.
# The hist() function will use an array of numbers to create a histogram, the array is sent into the function as an argument.
# For simplicity we use NumPy to randomly generate an array with 250 values, where the values will concentrate around 170, and the standard deviation is 10.
# x = np.random.normal(170, 10, 250)
# plt.hist(x)

# PIE CHART
# With Pyplot, you can use the pie() function to draw pie charts
y = np.array([35, 25, 25, 15])
mylabels = ["Apples", "Bananas", "Cherries", "Dates"]
plt.pie(y, labels = mylabels)


plt.show()