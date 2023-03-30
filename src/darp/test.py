import numpy as np
import sys
import time

from CalculateTrajectories import CalculateTrajectories
from darp import DARP
from kruskal import Kruskal
from turns import turns
from Visualization import visualize_paths


# darp_instance = DARP(10, 10, [0, 3, 9], [5, 6, 7], False, [0.2, 0.3, 0.5], True)
darp_instance = DARP(5, 5, [0, 2, 4], [7, 8], False, [0.2, 0.3, 0.5], True)
# Divide areas based on robots initial positions
darp_success , iterations = darp_instance.divideRegions()

if darp_success:
    print("DONE!")
else:
    print("Problem...")
