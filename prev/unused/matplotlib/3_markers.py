import matplotlib.pyplot as plt
import numpy as np

ypoints = np.array([3, 8, 1, 10])

plt.plot(ypoints, marker = 'o')
# Mark each point with a star
# plt.plot(ypoints, marker = '*')
plt.show()

# 'o' 	Circle 	
# '*' 	Star 	
# '.' 	Point 	
# ',' 	Pixel 	
# 'x' 	X 	
# 'X' 	X (filled) 	
# '+' 	Plus 	
# 'P' 	Plus (filled) 	
# 's' 	Square 	
# 'D' 	Diamond 	
# 'd' 	Diamond (thin) 	
# 'p' 	Pentagon 	
# 'H' 	Hexagon 	
# 'h' 	Hexagon 	
# 'v' 	Triangle Down 	
# '^' 	Triangle Up 	
# '<' 	Triangle Left 	
# '>' 	Triangle Right 	
# '1' 	Tri Down 	
# '2' 	Tri Up 	
# '3' 	Tri Left 	
# '4' 	Tri Right 	
# '|' 	Vline 	
# '_' 	Hline