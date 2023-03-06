import matplotlib.pyplot as plt
import numpy as np

ypoints = np.array([3, 8, 1, 10])

# linestyle -> change the style of the plotted line
plt.plot(ypoints, linestyle = 'solid', color = '#4CAF50', linewidth = 5.2)
# linestyles:
    # 'solid' (default) 	'-' 	
    # 'dotted' 	':' 	
    # 'dashed' 	'--' 	
    # 'dashdot' 	'-.' 	
    # 'None' 	'' or ' '
# color -> you can use hexadecimal color values
# linewidth -> floating number value
plt.show()