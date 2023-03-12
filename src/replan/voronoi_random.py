import numpy
from random import sample
import psutil
from itertools import product

import matplotlib.pyplot as plt


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
