
import numpy
from random import sample
import psutil
import variables as var
from cell import Cell
from itertools import product

def create_grid():
    for row in range(var.ROWS):
        var.grid.append([])
        for column in range(var.COLUMNS):
            var.grid[row].append(Cell(row,column))

def main():
    create_grid()
    sim_start_time = psutil.Process().cpu_times().user


    rand_list = sample(list(product(range(var.COLUMNS), repeat=2)), k=var.AGENT_COUNT)
    for count in range(var.AGENT_COUNT):
        row = rand_list[count][0]
        column = rand_list[count][1]
        
        

        var.grid[row][column].agent = True
        var.grid[row][column].agent_id = count
        var.grid[row][column].distance_matrix = var.grid[row][column].calc_distance_matrices()
        # print("the agent is at:", row, column)
        # print("distance matrix for agent",count,":\n", var.grid[row][column].distance_matrix)
        var.matrix_list.append(var.grid[row][column].distance_matrix)
        var.agent_locs.add((row,column))
    # check eac cell in matrix list; that holds every agent's distance matrix
    # and assign each cell to the lowest agent
    minimum_comparison_table = numpy.argmin((var.matrix_list), 0)
    # print('\nminimum value comparison:\n', minimum_comparison_table)
    print('\nagent locs length:', len(var.agent_locs))
    
    # generate random colors as many as the agent count
    for count in range(var.AGENT_COUNT):
        col = list(numpy.random.choice(range(256), size=3))     # random color creation
        var.colors.append(col)
    
    # for each item in grid, its agent id will be assigned from min table
    for row in range(var.ROWS):
        for column in range(var.COLUMNS):
            var.grid[row][column].agent_id = minimum_comparison_table[row][column]
    


    sim_end_time = psutil.Process().cpu_times().user
    print("Tot time=", sim_end_time - sim_start_time)
if __name__ == "__main__":
    main()
