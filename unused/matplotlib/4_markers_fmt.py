from plistlib import FMT_BINARY
import matplotlib.pyplot as plt
import numpy as np

ypoints = np.array([3, 8, 1, 10])


# shortcut string notation (fmt), is written with this syntax:
# marker|line|color
plt.plot(ypoints, 'o:r', ms=10, mec = 'b', mfc='g')
# marker value can be anything as shown in previous python example
# line values could be one of the following:
    # '-' 	Solid line 	
    # ':' 	Dotted line 	
    # '--' 	Dashed line 	
    # '-.' 	Dashed/dotted line
#  color values could be one of the following:
    # 'r' 	Red 	
    # 'g' 	Green 	
    # 'b' 	Blue 	
    # 'c' 	Cyan 	
    # 'm' 	Magenta 	
    # 'y' 	Yellow 	
    # 'k' 	Black 	
    # 'w' 	White
# ms -> markersize set the size of the markers
# mec -> markercolor for the edge of the markers (can accept hexadecimal values)
# mfc -> markercolor for the inside of the markers (can accept hexadecimal values)d

plt.show()