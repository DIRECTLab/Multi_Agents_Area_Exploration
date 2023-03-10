import pygame
import sys
import numpy as np
import time
import random
import psutil

COLUMNS = 400
ROWS = 400
# This sets the margin between each cell
MARGIN = 1
# This sets the WIDTH and HEIGHT of each grid location
CELL_WIDTH = 1
CELL_HEIGHT = 1
# Set the HEIGHT and WIDTH of the screen
WINDOW_WIDTH = COLUMNS * (CELL_WIDTH + MARGIN) + MARGIN
WINDOW_HEIGHT = ROWS * (CELL_HEIGHT + MARGIN) + MARGIN
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
# Define some colors
COLOR_BLACK = (0,0,0)
COLOR_GRAY = (50,50,50)
COLOR_GREEN = (0,255,0)
COLOR_PINK = (255,0,255)
AGENT_COUNT = 100

def random_color():
    color = list(np.random.choice(range(256), size=3))
    return color



matrix_list = []
agent_list = {}
coming_set = []
colors = []

agent_locs = set()
small_regions_cell_locs = set()

class Box:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.agent_id = None        # which agent is placed on a box 
        self.agent = False          # is the cell filled or not
        
    def draw(self, win, color):
        pygame.draw.rect(win,
                        color,
                        [(MARGIN + CELL_WIDTH) * self.column + MARGIN,
                        (MARGIN + CELL_HEIGHT) * self.row + MARGIN,
                        CELL_WIDTH,
                        CELL_HEIGHT])


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


def find_random(small_agent):
    #print("following agent is smaller than the average...", small_agent.row, small_agent.column, "which has", small_agent.responsible_cell_count, "cells.")
    #print("the agent id for the small voronoi region is:", small_agent.agent_id, "and here is the cells that belongs to this agent:")
    print("find_random is working")
    small_regions_cell_locs.clear()
    coming_set.clear()
    for row in range(ROWS):
        for column in range(COLUMNS):
            if grid[row][column].agent_id == small_agent.agent_id:
                #print(row,column)
                
                small_regions_cell_locs.add((row,column))
                coming_set.append(neighbours(row,column))

    #print("coming_set is:", coming_set)
    #for i in coming_set:
    #    print("i is: ",i)
    ##print everything including the small voronoi region's cells
    union_of_small_region = set().union(*coming_set)

    # now subtract the small subregion's voronoi cells as well as other agents locations from the big union set
    #print("agent_locs",agent_locs)
    #print("small_regions_cell_locs [voronoi regions]",small_regions_cell_locs)
    #print("coming_set",coming_set)

    union_of_subt = agent_locs | small_regions_cell_locs

    finalized_neighbors = union_of_small_region.difference(union_of_subt)
    #print("Here is the neighbors:", finalized_neighbors)
    random_index = random.choice(tuple(finalized_neighbors))
    #print("Randomly selected cell is:", random_index)
    return random_index


# Create a 2 dimensional array. A two dimensional array is simply a list of lists.
grid = []
for row in range(ROWS):
    # Add an empty array that will hold each cell in this row
    grid.append([])
    for column in range(COLUMNS):
        grid[row].append(Box(row,column))  # Append a cell

# print("INITIAL GRID\n", grid[3][2].agent_id)

# Set title of screen
pygame.display.set_caption("Auction Algorithm")

def main():
    index = -1
    global grid
    
    # -------- Main Program Loop -----------
    while True:
        time.sleep(0.05)
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                pygame.quit()   # we are done so we exit this loop
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    sim_start_time = psutil.Process().cpu_times().user


                    for count in range(AGENT_COUNT):
                        column = random.randint(0, COLUMNS-1)
                        row = random.randint(0, ROWS -1)
                        grid[row][column].agent = True
                        agent_list[count] = Agent(row,column)
                        # print("Agent",index,"is at:",row,column)
                        agent_list[count].distance_matrix = Agent.calc_distance_matrices(agent_list[count])
                        agent_list[count].agent_id = count
                        # print("Distance matrix for Agent",index,":\n", agent_list[count].distance_matrix)
                        matrix_list.append(agent_list[count].distance_matrix)
                        agent_locs.add((row,column))
                
                    for i in range(AGENT_COUNT):
                        col = random_color()
                        colors.append(col)
                    
                    minimum_comparison_table = np.argmin((matrix_list), 0)
                    print('\nminimum value comparison:\n', minimum_comparison_table)
                    
                    for row in range(ROWS):
                        for column in range(COLUMNS):
                            grid[row][column].agent = True
                            grid[row][column].agent_id = minimum_comparison_table[row][column]

                    sim_end_time = psutil.Process().cpu_times().user
                    print("Tot time=", sim_end_time - sim_start_time)
                    
                    

        # Set the screen background
        screen.fill(COLOR_BLACK)

        # Draw the grid
        for row in range(ROWS):
            for column in range(COLUMNS):
                
                box = grid[row][column]
                
                if grid[row][column].agent_id == None:
                    box.draw(screen, COLOR_GRAY)
                if box.agent:
                    box.draw(screen, COLOR_GREEN)

                for i in range(AGENT_COUNT):
                    if grid[row][column].agent_id == i:
                        box.draw(screen, colors[i])

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

main()
