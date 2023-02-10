import pygame
import sys
import numpy as np
import time
import random

COLUMNS = 10
ROWS = 10
# This sets the margin between each cell
MARGIN = 2
# This sets the WIDTH and HEIGHT of each grid location
CELL_WIDTH = 15
CELL_HEIGHT = 15
# Set the HEIGHT and WIDTH of the screen
WINDOW_WIDTH = COLUMNS * (CELL_WIDTH + MARGIN) + MARGIN
WINDOW_HEIGHT = ROWS * (CELL_HEIGHT + MARGIN) + MARGIN
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
# Define some colors
COLOR_BLACK = (0,0,0)
COLOR_WHITE = (255,255,255)

agent_list, agent_locs, all_bids = dict(), dict(), dict()
wall_list, colors, visited_cells_list = list(), list(), list()
all_areas_explored = False
all_dics_are_empty = False

class Box:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.agent = False              # is the cell already visited or not visited (mark it as either False or True)
        self.agent_id = None            # which agent is placed on a selected cell
        self.wall = False               # is the cell already visited or not visited (mark it as either False or True)
        
    def draw(self, win, color):
        pygame.draw.rect(win,
                        color,
                        [(MARGIN + CELL_WIDTH) * self.column + MARGIN,
                        (MARGIN + CELL_HEIGHT) * self.row + MARGIN,
                        CELL_WIDTH,
                        CELL_HEIGHT])

class agent(Box):
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.agent_id = None
        self.neighbors = {}
        self.win_cells = {}
        self.distance_matrix = None
        self.start_energy = random.randint(10, 100)

    def find_my_neighbours(self, all_agent_locations, wall_locs):
        self.neighbors.clear()
        pn = [(self.row-1, self.column), (self.row+1, self.column), (self.row-1, self.column-1), (self.row, self.column-1),
            (self.row+1, self.column-1), (self.row-1, self.column+1), (self.row, self.column+1), (self.row+1, self.column+1)]
        
        for i, t in enumerate(pn):
            if t[0] < 0 or t[1] < 0 or t[0] >= ROWS or t[1] >= COLUMNS:
                pn[i] = None
            else:
                # if the neighbor within the grid, then calculate distance towards those agents
                dist = np.sqrt((self.row - t[0])**2 + (self.column - t[1])**2)
                # and generate the neighbors for each agent(key:value --> (row,column):distance)
                self.neighbors[(t[0], t[1])] = dist
        
        # calculate the movable cells for an agent by removing "agent_locations and wall_locs" from the full neighbor list
        subtract_res = {k:[v] for k,v in self.neighbors.items() if(k not in all_agent_locations and k not in wall_locs)}
        self.neighbors.clear()
        # new neighbors for the agents now is subtract_res
        self.neighbors = subtract_res
        
        
        
    # calculate the distance matrix(full grid) for each agent based on the agent's location
    def calc_distance_matrices(self):
        x_arr, y_arr = np.mgrid[0:ROWS, 0:COLUMNS]
        cell = (self.row, self.column)
        dists = np.sqrt((x_arr - cell[0])**2 + (y_arr - cell[1])**2)
        return dists
    
    # calculate the distance from the agent to the won cell
    def calc_won_distance(self, row, column):
        agent_loc = (self.row, self.column)
        distance_of_movement = np.sqrt((agent_loc[0] - row)**2 + (agent_loc[1] - column)**2)
        return distance_of_movement

    # each agent send bids to its neighbors in each iteration
    def send_bid(self):
        global all_areas_explored
        
        # If the agent only has one neighbor, offer a bid based on the neighbor is visited or not
        if(len(self.neighbors)==1):
            for key, value in self.neighbors.items():
                # if there is only one neighbor, which is previously visited, then offer a bid (0)
                if(grid[key[0]][key[1]].agent == True):
                    self.neighbors[key].extend([0, self.agent_id])
                # else: use the following formula to bid to a neighbor
                else:
                    self.neighbors[key].extend([(1/self.start_energy) * (1 / (0.5 * value[0])), self.agent_id])
        # If an agent has more than one neighbor, offer a bid for each neighbors based on the neighbors are visited or not
        else:
            # use the following count variable for the following purpose:
            # check one by one each neighbors, if the selected neighbor is previously visited, increase the counter
            # if all neighbors are previously visited, then that agent should send a bid to the most profitable unexplored cell
            count = 0
            # copy the self.neighbors dictionary to prevent runtime error since we are adding new elements to the neighbors dictionary during the iteration
            neighbors_copy = tuple(self.neighbors.items())
            # for each neighbor of an agent, check their neighbors whether a neighbor is previosly visited or not
            for key, value in neighbors_copy:
                # if a neighbor is previosly visited, offer something less
                if(grid[key[0]][key[1]].agent == True):
                    self.neighbors[key].extend([0, self.agent_id])
                    # if all neighbors for the agent are previously visited or has an agent in one one of the neighbor locs, then bid to other cells that are not visited
                    count = count + 1
                    if(count == len(self.neighbors)):
                        # bring visited cells ==> (visited + agent_locs)
                        visited_cells = bring_all_visited_locations()
                        # print("For agent",self.agent_id,"located at", self.row, self.column, "here are the all visited cells:", visited_cells)
                        # for the agent, calculate distance matrix for all grid
                        self.distance_matrix = self.calc_distance_matrices()
                        # print(self.distance_matrix)
                        # mark the visited cell locations as "None" since we are interested in to find lowest cost unvisited cell
                        for i in visited_cells:
                            row_c,column_c = i[0],i[1]
                            self.distance_matrix[row_c][column_c] = None
                        # if the distance matrix is full of "nan" values, then "all_areas_explored" flag will turn to TRUE
                        if(np.isnan(self.distance_matrix).all()):
                            all_areas_explored = True
                            break
                        # below two lines are getting the min value from unvisited cells and assign them into the surrounded agent
                        # min_value_among_unv_cells = np.unravel_index(np.nanargmin(self.distance_matrix, axis=None), self.distance_matrix.shape)
                        # self.neighbors[min_value_among_unv_cells] = [np.nanmin(self.distance_matrix), ((1/self.start_energy) * ((1 / np.nanmin(self.distance_matrix)) + 1))]
                # if the neighbor is previously not visited, then offer something higher
                elif(grid[key[0]][key[1]].agent == False):
                    self.neighbors[key].extend([(1/self.start_energy) * (1 / value[0]), self.agent_id])
    # this function send a zero bid to a neighbor when it does not have an energy left
    def zero_bid(self):
        for key, value in self.neighbors.items():
            self.neighbors[key].extend([0, self.agent_id])

def bring_all_visited_locations():
    # print("\n\nwhere are the zeros:")
    for row in range(ROWS):
        print()
        for column in range(COLUMNS):
            if(grid[row][column].agent == True or grid[row][column].wall == True):
                # print("There is either an agent or visited cell at this locatio:",row,column)
                visited_cells_list.append((row,column))
    return visited_cells_list

# def current_matrix_state_in_terminal():
#     # print("\n\nhere is the current matrix state:")
#     for row in range(ROWS):
#         print()
#         for column in range(COLUMNS):
#             if grid[row][column].agent == True:
#                 print(1, end = ' ')
#             else:
#                 print(0, end = ' ')


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
    global grid
    global all_dics_are_empty
    index = -1

    # -------- Main Program Loop -----------
    while True:
        # time.sleep(0.05)
        for event in pygame.event.get():  # User did something
            
            if event.type == pygame.QUIT:  # If user clicked close
                pygame.quit()   # we are done so we exit this loop
                sys.exit()

            # if there is a mouse left button click, place an agent
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if(event.button==1):
                    index = index + 1
                    pos = pygame.mouse.get_pos()
                    column = pos[0] // (CELL_WIDTH + MARGIN)
                    row = pos[1] // (CELL_HEIGHT + MARGIN)
                    box = grid[row][column]
                    box.agent = True
                    box.agent_id = index
                    random_color = list(np.random.choice(range(256), size=3))
                    colors.append(random_color)
                    # agent_list = {([0], agent_obj_0), ([1], agent_obj_1), ...}
                    agent_list[index] = agent(row,column)
                    agent_list[index].agent_id = index
                    # agent_locs = {([row,column], agent_id)}
                    agent_locs[(row, column)] = index
                    print("Agent",index,"'s energy is:", agent_list[index].start_energy)

            # if there is a mouse right button click constantly, draw the wall onto grid
            elif event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                column = pos[0] // (CELL_WIDTH + MARGIN)
                row = pos[1] // (CELL_HEIGHT + MARGIN)
                
                # if right click mouse is TRUE within the grid size, then run followings
                if event.buttons[2] and row < ROWS and column < COLUMNS:
                    grid[row][column].wall = True
                    if((row,column) not in wall_list):
                        wall_list.append((row,column))
            
            # based on the entered keyboard key, run different things
            if event.type == pygame.KEYDOWN:
                

                
                # if the user clicks n, run followings
                if event.key == pygame.K_n:
                        # if an agent does not win any cell, increase empty_dic_counter
                        # if nobody wins anything, then it is one of the condition to end the program
                        empty_dic_counter = 0



                        # for each agent in agent_list: find its neighbors, calculate distance to each neighbor, remove the wall & agent locs from neighbor_list
                        for i in agent_list:
                            agent_list[i].find_my_neighbours(agent_locs, wall_list)
                            
                            if(agent_list[i].start_energy > 0):
                                agent_list[i].send_bid()
                            else:
                                # print("You are negative. You cannot bid.")
                                agent_list[i].zero_bid()
                        
                            # for each neighbor cell that gets the bid:
                            # collect offers at one location point(all_bids)
                            # ex: key(cell), value(bids) ---> (1, 1), [[1.4142135623730951, 0.01860807318911967, 0], [1.0, 0.03333333333333333, 1]]
                            for j, k in agent_list[i].neighbors.items():
                                try:
                                    all_bids[j].append(k)
                                except:
                                    all_bids[j] = [k]
                                print(j, all_bids[j])
                        



                        # which cell is won by which agent
                        for x in all_bids:
                            print("for the cells", x, "the bids are as follows:", all_bids[x])
                            a = np.array(all_bids[x])
                            highestbid = a.max(axis=0)[1]
                            # print("here is the highest_bid", highestbid)
                            highestbid_index = a.argmax(axis=0)[1]
                            # among the neighbor cells, assign one cell at a time to the highest bidder
                            # which agent win which cells?
                            # print("the cell", x, "is won with max bid", highestbid, "by the agent:",all_bids[x][highestbid_index][2])
                            # now the agent either will go to cell that it sent a higher bid
                            # list the won cells for each agent
                            if(highestbid>0.0):
                                agent_list[all_bids[x][highestbid_index][2]].win_cells[x] = highestbid
                        # for i in agent_list:
                        #     print("Agent",i,"win cells with their bids:", agent_list[i].win_cells)
                        agent_locs.clear()
                        



                        # among the win cells where the agent should move
                        for i in agent_list:
                            if agent_list[i].win_cells:
                                
                                max_item_value = max(agent_list[i].win_cells.values())
                                tup = [k for k, v in agent_list[i].win_cells.items() if v == max_item_value]
                                
                                if len(tup) > 1:
                                    ll = random.choice(tup)
                                    row_val, column_val = ll
                                else:
                                    row_val, column_val = tup[0]

                                # print("where is the agent currently:", agent_list[i].row, agent_list[i].column)
                                distance_of_move = agent_list[i].calc_won_distance(row_val, column_val)

                                if(agent_list[i].start_energy >= (distance_of_move + 5)):
                                    grid[row_val][column_val].agent_id = i
                                    grid[row_val][column_val].agent = True
                                    agent_list[i].row = row_val
                                    agent_list[i].column = column_val
                                    # update the agent locs after we move the agents to new locs
                                    agent_locs[(agent_list[i].row,agent_list[i].column)] = agent_list[i].agent_id


                                    # print("how are the win_cells now for agent", i,":::",agent_list[i].win_cells)
                                    # print("the cell that the agent moves is:", row_val, column_val)
                                    
                                    # agent_list[i].start_energy = agent_list[i].start_energy - (distance_to_win_cell + cleaning_value)
                                    agent_list[i].start_energy = agent_list[i].start_energy - (distance_of_move + 5)
                                    # print("new energy value for agent", i, "after the visitation:", agent_list[i].start_energy)
                                else:
                                    agent_locs[(agent_list[i].row,agent_list[i].column)] = agent_list[i].agent_id
                                    agent_list[i].start_energy = 0

                            # else, for each agent that does not have a win cell, increase empty_dic_counter
                            else:
                                empty_dic_counter = empty_dic_counter + 1
                                if(empty_dic_counter == index + 1):
                                    all_dics_are_empty = True
                            # print("After the iteration, the energies are as follows for agent",i,":::",agent_list[i].start_energy)

                        
                        
                        
                        
                        all_bids.clear()
                        for i in agent_list:
                            agent_list[i].win_cells.clear()

                        if(all_areas_explored | all_dics_are_empty):
                            print("all_areas_explored",all_areas_explored)
                            print("all_dics_are_empty",all_dics_are_empty)
                            break
                            
                            
                        
                        # step_counter = step_counter+1
                    # pygame.image.save(screen, "final.png")
                
                # if event.key == pygame.K_t:
                #     print(end - start)
                #     pygame.image.save(screen, "final.png")




        # Set the screen background
        screen.fill(COLOR_BLACK)
        # Draw the grid
        for row in range(ROWS):
            for column in range(COLUMNS):
                
                box = grid[row][column]
                box.draw(screen, COLOR_WHITE)
                
                # if there is a wall is drawn into canvas, color it with black
                if box.wall:
                    box.draw(screen, COLOR_BLACK)
                
                # if there is an agent is drawn onto canvas, color it based on the "agent_id"
                for i in range(index+1):
                    if box.agent_id == i:
                        box.draw(screen, colors[i])
                
        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
main()
