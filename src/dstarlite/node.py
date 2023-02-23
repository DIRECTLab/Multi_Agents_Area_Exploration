import numpy as np


class Node:
    """
    Class represents a grid search node.
    """
    def __init__(self, position, g_value=np.inf, rhs_value=np.inf, parent=None):
        # position on the map
        self.row, self.column = position
        self.position = position

        # values for the search
        self.g_value = g_value
        self.rhs_value = rhs_value

        # node to backtrace
        self.parent = parent

    def __eq__(self, other):
        return (self.row == other.row) and (self.column == other.column)

    def __lt__(self, other):
        return (self.row < other.row) or (self.row == other.row and self.column < other.column)
