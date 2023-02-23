import itertools
import numpy as np
import re

TRANSITION_COST = 1
WALL = '#'
PASSABLE = '.'


class Grid:
    """
    Class to store actual grid and grid observed by the agent.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.is_wall_cell_actual = np.zeros((height, width), dtype=bool)
        self.is_wall_cell_observed = np.zeros((height, width), dtype=bool)
        
        self.is_passable_cell_actual = np.zeros((height, width), dtype=bool)
        self.is_passable_cell_observed = np.zeros((height, width), dtype=bool)

    def read_from_string(self, grid_string):
        """
        Read actual grid from a given string.
        """
        row = None
        grid_string_processed = re.sub(' ', '', grid_string.strip())
        print(grid_string_processed)
        for row, line in enumerate(grid_string_processed.split('\n')):
            if len(line) != 0:
                column = None
                for column, symbol in enumerate(line):
                    if symbol == PASSABLE:
                        self.is_wall_cell_actual[row][column] = False
                        self.is_passable_cell_actual[row][column] = True
                    elif symbol == WALL:
                        self.is_wall_cell_actual[row][column] = True
                    else:
                        continue
                if column is None or column != self.width - 1:
                    raise ValueError('Grid width is {}, but expected value is {}'.format(column, self.width))
        if row is None or row != self.height - 1:
            raise ValueError("Grid height is {}, but expected value is {}".format(row, self.height))

    def set_grid_from_array(self, actual_grid):
        assert actual_grid.shape[0] == self.height and actual_grid.shape[1] == self.width
        self.is_wall_cell_actual = actual_grid

    def in_bounds(self, row, column):
        return 0 <= row < self.height and 0 <= column < self.width

    def is_traversable(self, row, column):
        """
        Check node in observed grid.
        """
        return not self.is_wall_cell_observed[row][column]

    def get_neighbors(self, position_row, position_column):
        """
        Return neighbors calculated by observed grid,
        does not take walls into account since walls are presented by cost
        """
        neighbors = []
        for d_row, d_column in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            if self.in_bounds(position_row + d_row, position_column + d_column):
                neighbors.append((position_row + d_row, position_column + d_column))

        return neighbors

    def calculate_cost(self, node_from, node_to):
        """
        Get edge cost calculated by observed grid.for two nodes of type Node.
        """
        for node in (node_from, node_to):
            if not self.in_bounds(node.row, node.column) or \
                    not self.is_traversable(node.row, node.column):
                return np.inf
        return TRANSITION_COST

    def observe(self, position_row, position_column, observe_range=2):
        """
        Update grid observed by the agent by coping values from actual grid.
        """
        new_walls_positions = []
        passable_observed_walls = []
        for d_row, d_column in itertools.product(
                range(-observe_range, observe_range + 1), range(-observe_range, observe_range + 1)
        ):
            row = position_row + d_row
            column = position_column + d_column
            if self.in_bounds(row, column):
                if self.is_wall_cell_actual[row, column] and not self.is_wall_cell_observed[row, column]:
                    new_walls_positions.append((row, column))
                    # print("new_walls_positions", new_walls_positions)
                elif not self.is_wall_cell_actual[row, column]:
                    passable_observed_walls.append((row,column))
                    # print("passable_observed_walls",passable_observed_walls)
                
                self.is_wall_cell_observed[row, column] = self.is_wall_cell_actual[row, column]
                self.is_passable_cell_observed[row, column] = self.is_passable_cell_actual[row, column]

        return new_walls_positions