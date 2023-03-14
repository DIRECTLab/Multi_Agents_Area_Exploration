import numpy
from random import sample
import psutil
from itertools import product
import numpy as np

import matplotlib.pyplot as plt

class Rand_Voronoi:       
    def get_random_unnknown(self):
        unknown_points = np.argwhere(self.agent_map == self.cfg.UNKNOWN)
        unknown_points_assigned = []
        for point in unknown_points:
            if tuple(point) in self.assigned_points:
                unknown_points_assigned.append(point)
        if len(unknown_points_assigned) == 0:
            # return self.get_random_point()
            print("get_random_unnknown(): No unknown points")
            # set goal as current position
            self.plan = []
            self.area_completed = True
            return [-1,-1]
        elif len(unknown_points_assigned) == 1:
            return (unknown_points_assigned[0][1], unknown_points_assigned[0][0])
        # choose a random UNKNOWN
        idx = np.random.randint(len(unknown_points_assigned))
        return (unknown_points_assigned[idx][1], unknown_points_assigned[idx][0])
    
    def get_random_frontier(self):
        frontier_points = np.argwhere(self.agent_map == self.cfg.FRONTIER)
        frontier_points_assigned = []
        for point in frontier_points:
            if tuple(point) in self.assigned_points:
                frontier_points_assigned.append(point)
        if len(frontier_points_assigned) == 0:
            return self.get_random_unnknown()
        elif len(frontier_points_assigned) == 1:
            return (frontier_points_assigned[0][1], frontier_points_assigned[0][0])
        # choose a random frontier
        idx = np.random.randint(len(frontier_points_assigned))
        return (frontier_points_assigned[idx][1], frontier_points_assigned[idx][0])
    
    def get_goal_method(self):
        return self.get_random_frontier()

class Closest_Voronoi():
    def get_closet_unknown(self):
        # finds the classes unknown point
        unknown_points = np.argwhere(self.agent_map == self.cfg.UNKNOWN)
        unknown_points_assigned = []
        for point in unknown_points:
            if tuple(point) in self.assigned_points:
                unknown_points_assigned.append(point)
        if len(unknown_points_assigned) == 0:
            # return self.get_random_point()
            print("get_closet_unknown(): No unknown points")
            # set goal as current position
            self.plan = []
            self.area_completed = True
            return [-1,-1]
        elif len(unknown_points_assigned) == 1:
            return (unknown_points_assigned[0][1], unknown_points_assigned[0][0])
        # choose the closest UNKNOWN
        nest_point = self.get_closest_point_rc(unknown_points_assigned)
        return (nest_point[1], nest_point[0])

    def get_closet_frontier(self):
        frontier_points = np.argwhere(self.agent_map == self.cfg.FRONTIER)
        frontier_points_assigned = []
        for point in frontier_points:
            if tuple(point) in self.assigned_points:
                frontier_points_assigned.append(point)
        if len(frontier_points_assigned) == 0:
            return self.get_closet_unknown()
        elif len(frontier_points_assigned) == 1:
            return (frontier_points_assigned[0][1], frontier_points_assigned[0][0])
        # choose the closest frontier
        nest_point = self.get_closest_point_rc(frontier_points_assigned)
        return (nest_point[1], nest_point[0])

    def get_goal_method(self):
        return self.get_closet_frontier()


AGENT_COUNT = 100
ROWS = 500
COLUMNS = 500
matrix_list, coming_set, colors, grid = list(), list(), list(), list()
agent_locs = set()

class Cell:
    def __init__(self, row, column):        
        self.pos_row = row
        self.pos_column = column
        self.agent = False          # is there any agent over a cell
        self.agent_id = None        # which agent is placed on a box 
        self.distance_matrix = None
    def calc_distance_matrices(self):
        x_arr, y_arr = numpy.mgrid[0:ROWS, 0:COLUMNS]
        cell = (self.pos_row, self.pos_column)
        dists = numpy.sqrt((x_arr - cell[0])**2 + (y_arr - cell[1])**2)
        return dists

def create_grid():
    for row in range(ROWS):
        grid.append([])
        for column in range(COLUMNS):
            grid[row].append(Cell(row,column))

def main():
    fig, ax = plt.subplots()
    create_grid()
    sim_start_time = psutil.Process().cpu_times().user
    rand_list = sample(list(product(range(COLUMNS), repeat=2)), k=AGENT_COUNT)
    for count in range(AGENT_COUNT):
        row = rand_list[count][0]
        column = rand_list[count][1]
        grid[row][column].agent = True
        grid[row][column].agent_id = count
        grid[row][column].distance_matrix = grid[row][column].calc_distance_matrices()
        # print("the agent", count, "is at:", row, column)
        # print("distance matrix for agent",count,":\n", var.grid[row][column].distance_matrix)
        matrix_list.append(grid[row][column].distance_matrix)
        agent_locs.add((row,column))
        ax.scatter(column, row, color='red')
    # check eac cell in matrix list; that holds every agent's distance matrix
    # and assign each cell to the lowest agent
    minimum_comparison_table = numpy.argmin((matrix_list), 0)
    ax.matshow(minimum_comparison_table)
            
    plt.show()
    print('\nminimum value comparison:\n', minimum_comparison_table)
    print("\nagent locs length:", len(agent_locs))
    # generate random colors as many as the agent count
    for count in range(AGENT_COUNT):
        col = list(numpy.random.choice(range(256), size=3))     # random color creation
        colors.append(col)    
    # for each item in grid, its agent id will be assigned from min table
    for row in range(ROWS):
        for column in range(COLUMNS):
            grid[row][column].agent_id = minimum_comparison_table[row][column]
    sim_end_time = psutil.Process().cpu_times().user
    print("Tot time: ", sim_end_time - sim_start_time)
if __name__ == "__main__":
    main()
