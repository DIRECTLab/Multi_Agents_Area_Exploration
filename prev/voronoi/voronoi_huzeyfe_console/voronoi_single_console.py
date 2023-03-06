import numpy as np
from random import sample
import psutil
from itertools import product

AGENT_COUNT = 100
ROWS = 400
COLUMNS = 400
matrix_list, coming_set, colors, grid = list(), list(), list(), list()
agent_locs = set()
agent_list = dict()

class Box:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.agent_id = None        # which agent is placed on a box 
        self.agent = False          # is the cell filled or not


class Agent:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.agent_id = None
        self.distance_matrix = None
    
    def calc_distance_matrices(self):
        x_arr, y_arr = np.mgrid[0:ROWS, 0:COLUMNS]
        cell = (self.row, self.column)
        dists = np.sqrt((x_arr - cell[0])**2 + (y_arr - cell[1])**2)
        return dists


    
def neighbours(x, y):
    pn = [(x-1, y), (x+1, y), (x-1, y-1), (x, y-1),
          (x+1, y-1), (x-1, y+1), (x, y+1), (x+1, y+1)]
    for i, t in enumerate(pn):
        if t[0] < 0 or t[1] < 0 or t[0] >= ROWS or t[1] >= COLUMNS:
            pn[i] = None
    return {c for c in pn if c is not None}

for row in range(ROWS):
    grid.append([])
    for column in range(COLUMNS):
        grid[row].append(Box(row,column))  # Append a cell

def main():
    global grid
    sim_start_time = psutil.Process().cpu_times().user

    rand_list = sample(list(product(range(COLUMNS), repeat=2)), k=AGENT_COUNT)
    for count in range(AGENT_COUNT):
        row = rand_list[count][0]
        column = rand_list[count][1]
        grid[row][column].agent = True
        agent_list[count] = Agent(row,column)
        # print("Agent",index,"is at:",row,column)
        agent_list[count].distance_matrix = Agent.calc_distance_matrices(agent_list[count])
        agent_list[count].agent_id = count
        # print("Distance matrix for Agent",index,":\n", agent_list[count].distance_matrix)
        matrix_list.append(agent_list[count].distance_matrix)
        agent_locs.add((row,column))
    
    minimum_comparison_table = np.argmin((matrix_list), 0)
    # print('\nminimum value comparison:\n', minimum_comparison_table)
    print('\nagent locs length:', len(agent_locs))
    
    for row in range(ROWS):
        for column in range(COLUMNS):
            grid[row][column].agent = True
            grid[row][column].agent_id = minimum_comparison_table[row][column]

    sim_end_time = psutil.Process().cpu_times().user
    print("Tot time=", sim_end_time - sim_start_time)
                    

main()
