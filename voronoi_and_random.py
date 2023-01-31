import pygame
import sys
import numpy as np
import time
import random

COLUMNS = 50
ROWS = 50
# This sets the margin between each cell
MARGIN = 3
# This sets the WIDTH and HEIGHT of each grid location
CELL_WIDTH = 10
CELL_HEIGHT = 10
# Set the HEIGHT and WIDTH of the screen
WINDOW_WIDTH = COLUMNS * (CELL_WIDTH + MARGIN) + MARGIN
WINDOW_HEIGHT = ROWS * (CELL_HEIGHT + MARGIN) + MARGIN
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
# Define some colors
COLOR_BLACK = (0,0,0)
COLOR_GRAY = (50,50,50)
COLOR_GREEN = (0,255,0)
COLOR_PINK = (255,0,255)

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
        self.responsible_cell_count = 0
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
            # set agent locs
            elif event.type == pygame.MOUSEBUTTONDOWN:
                index = index + 1
                # print("index value is: ", index)
                # User clicks the mouse. Get the position
                pos = pygame.mouse.get_pos()
                # Change the x/y screen coordinates to grid coordinates
                column = pos[0] // (CELL_WIDTH + MARGIN)
                row = pos[1] // (CELL_HEIGHT + MARGIN)
                
                # Set that location to one
                grid[row][column].agent = True

                agent_list[index] = Agent(row,column)
                print("Agent",index,"is at:",row,column)
                # start working on distance matrix
                agent_list[index].distance_matrix = Agent.calc_distance_matrices(agent_list[index])
                agent_list[index].agent_id = index
                print("Distance matrix for Agent",index,":\n", agent_list[index].distance_matrix)
                # add all distance matrixes of agents into one giant matrix table for later comparisons
                matrix_list.append(agent_list[index].distance_matrix)
                agent_locs.add((row,column))

            # check if a key in the keyboard is pressed
            if event.type == pygame.KEYDOWN:
                
                # if 'c' is pressed
                # clean everything to start again 
                if event.key == pygame.K_c:
                    print("clearing everything...")
                    index = -1
                    matrix_list.clear()
                    agent_list.clear()
                    for row in range(ROWS):
                        for column in range(COLUMNS):            
                            grid[row][column].agent_id = None
                            grid[row][column].agent = False



                # if 'a' is pressed
                # find voronoi regions as follow:
                # compare all distance matrixes to decide which agent should cover what part of the map
                elif event.key == pygame.K_a:
                    #print("Here is the matrix_list table...\n", matrix_list)
                    #assign each cell to closest agent

                    # generate random colors for the entered number of agents
                    for i in range(index+1):
                        col = random_color()
                        colors.append(col)

                    minimum_comparison_table = np.argmin((matrix_list), 0)
                    print('\nminimum value comparison:\n', minimum_comparison_table)
                    
                    for row in range(ROWS):
                        for column in range(COLUMNS):
                            grid[row][column].agent = True                                          # each Box(cell) has an agent(TRUE) or notF(FALSE)
                            grid[row][column].agent_id = minimum_comparison_table[row][column]      # the agent_id of a cell is coming from min_table
                            #based on the agent id, increase the responsible cell count
                            #print("here is the agent ids for each cell....", grid[row][column].agent_id)
                            agent_list[grid[row][column].agent_id].responsible_cell_count = agent_list[grid[row][column].agent_id].responsible_cell_count + 1
                    
                    for i in agent_list:
                        print("Agent", i, "has", agent_list[i].responsible_cell_count, "cells.")
                    print("Average cells count:", int(ROWS*COLUMNS/(index+1)))


                #find two agent's combined neighbour cell locations
                #NO WORKING PURPOSE CURRENTLY - JUST FOR DEMONSTRATION
                elif event.key == pygame.K_n:
                    # index keeps the number of agents (ex: index is 1(0 and 1) when 2 agent is selected)
                    for i in range(index+1):
                        # put each agent's neighbors into the comming_set (agent_0 neighbors, agent_1 neighbors, etc.)
                        print("Agent", i, "th location is:", agent_list[i].row, agent_list[i].column, "Now adding this agent's neighbours into coming_set...")
                        coming_set.append(neighbours(agent_list[i].row, agent_list[i].column))
                    # print the union of two given set (mutual neighbors of 2 agents)
                    print("\nAgent 0 and 1th mutual neighbors are as follows:\n", coming_set[0]|coming_set[1])

                
                # find small voronoi region's neighbors
                elif event.key == pygame.K_v:
                    
                    new_list = []
                    for i in agent_list:
                        print(agent_list[i].responsible_cell_count)
                        new_list.append(agent_list[i].responsible_cell_count)

                    #print(all(i >= int(ROWS*COLUMNS/(index+1)) for i in new_list))
                        
                    
                    i=0
                    while True:
                        #time.sleep(0.5)
                        
                        for i in agent_list:
                            print("agent_list[i].responsible_cell_count",agent_list[i].responsible_cell_count)
                        
                            if(agent_list[i].responsible_cell_count < int(ROWS*COLUMNS/(index+1))):
                                ran = find_random(agent_list[i])
                                agent_list[grid[ran[0]][ran[1]].agent_id].responsible_cell_count = agent_list[grid[ran[0]][ran[1]].agent_id].responsible_cell_count - 1
                                agent_list[i].responsible_cell_count = agent_list[i].responsible_cell_count + 1
                                new_list[i] = new_list[i]+1
                                new_list[grid[ran[0]][ran[1]].agent_id] = new_list[grid[ran[0]][ran[1]].agent_id]-1
                                grid[ran[0]][ran[1]].agent_id = i

                        if(all(i >= int(ROWS*COLUMNS/(index+1)) for i in new_list)):
                            print(new_list)
                            break

                    for i in agent_list:
                        print("Agent", i, "has", agent_list[i].responsible_cell_count, "cells.")
                    print("Average cells count:", int(ROWS*COLUMNS/(index+1)))

                #elif event.key == pygame.K_b:
                #    for row in range(ROWS):
                #        for column in range(COLUMNS):
                #            print(grid[row][column].agent_id)


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

                for i in range(index+1):
                    if grid[row][column].agent_id == i:
                        box.draw(screen, colors[i])

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

main()
