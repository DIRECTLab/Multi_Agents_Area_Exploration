import pygame
import sys
import numpy as np
import time
import random

COLUMNS = 10
ROWS = 10
# This sets the margin between each cell
MARGIN = 3
# This sets the WIDTH and HEIGHT of each grid location
CELL_WIDTH = 20
CELL_HEIGHT = 20
# Set the HEIGHT and WIDTH of the screen
WINDOW_WIDTH = COLUMNS * (CELL_WIDTH + MARGIN) + MARGIN
WINDOW_HEIGHT = ROWS * (CELL_HEIGHT + MARGIN) + MARGIN
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
# Define some colors
COLOR_BLACK = (0,0,0)
COLOR_GRAY = (50,50,50)
COLOR_GREEN = (0,255,0)

agent_list, agent_locs = dict(),dict()
all_bids = dict()
colors = list()
unvisited_cells = list()
all_areas_explored = False
all_dics_are_empty = False

class Box:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.agent = False          # is the cell already visited or not visited (mark it as either False or True)
        self.agent_id = None        # which agent is placed on a selected cell
        
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
        self.start_energy = random.randint(2500, 5000)

    # calculate the distance matrix for each agent based on the agent's location
    def calc_distance_matrices(self):
        x_arr, y_arr = np.mgrid[0:ROWS, 0:COLUMNS]
        cell = (self.row, self.column)
        dists = np.sqrt((x_arr - cell[0])**2 + (y_arr - cell[1])**2)
        return dists

    # calculate the neighbor distances for an agent
    def calc_neighbor_distance(self, neighbor_locs):
        agent_loc = (self.row, self.column)
        self.neighbors.clear()
        for i in neighbor_locs:
            dists = np.sqrt((agent_loc[0] - i[0])**2 + (agent_loc[1] - i[1])**2)
            self.neighbors[(i[0], i[1])] = dists
    
    # calculate the distance from the agent to the won cell
    def calc_won_distance(self, row, column):
        agent_loc = (self.row, self.column)
        distance_of_movement = np.sqrt((agent_loc[0] - row)**2 + (agent_loc[1] - column)**2)
        return distance_of_movement

    # calculate the movable cells for an agent by removing agent_locations from the full neighbor list
    def movable_cells(self, all_agent_locations):
        # subtract for each agent
        # all_movable_neighbor_options - all_agent_locations
        subtract_res = {k:[v] for k,v in self.neighbors.items() if k not in all_agent_locations}
        # print("self.neighbors2",self.neighbors)
        self.neighbors.clear()
        self.neighbors = subtract_res

def random_color():
    color = list(np.random.choice(range(256), size=3))
    return color

def find_neighbours(x, y):
    pn = [(x-1, y), (x+1, y), (x-1, y-1), (x, y-1),
          (x+1, y-1), (x-1, y+1), (x, y+1), (x+1, y+1)]
    for i, t in enumerate(pn):
        if t[0] < 0 or t[1] < 0 or t[0] >= ROWS or t[1] >= COLUMNS:
            pn[i] = None
    return [c for c in pn if c is not None]

def current_matrix_state():
    # print("\n\nhere is the current matrix state:")
    for row in range(ROWS):
        print()
        for column in range(COLUMNS):
            if grid[row][column].agent == True:
                print(1, end = ' ')
            else:
                print(0, end = ' ')

def bring_all_visited_locations():
    # print("\n\nwhere are the zeros:")
    for row in range(ROWS):
        print()
        for column in range(COLUMNS):
            if grid[row][column].agent == True:
                # print("There is either an agent or visited cell at this locatio:",row,column)
                unvisited_cells.append((row,column))
    return unvisited_cells
                

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
    # print("\n****************************************\n")

    # -------- Main Program Loop -----------
    while True:
        # problem: comment the sleep function once this is done.
        time.sleep(0.05)
        for event in pygame.event.get():  # User did something
            
            if event.type == pygame.QUIT:  # If user clicked close
                pygame.quit()   # we are done so we exit this loop
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                index = index + 1
                # User clicks the mouse. Get the position
                pos = pygame.mouse.get_pos()
                # Change the x/y screen coordinates to grid coordinates
                column = pos[0] // (CELL_WIDTH + MARGIN)
                row = pos[1] // (CELL_HEIGHT + MARGIN)
                # Set that location to one
                grid[row][column].agent = True
                grid[row][column].agent_id = index
                # create random colors for each mouse pressed
                # and assign these colors to each agent
                col = random_color()
                colors.append(col)
                
                agent_list[index] = agent(row,column)
                agent_list[index].agent_id = index
                # print("Agent list", index, "row and column:",agent_list[index].row,agent_list[index].column)

                # collect all agents locations into one specific set object that will be used for subtraction
                # can we achieve the same thing without this?
                agent_locs[(agent_list[index].row,agent_list[index].column)] = agent_list[index].agent_id
                current_matrix_state()
                print("Agent",index,"'s energy is:", agent_list[index].start_energy)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    print("hello")
                    agent_count =10
                    list_of_locs = list()
                    while(len(list_of_locs) < agent_count):
                        row_x = random.randint(0, ROWS-1)
                        column_x = random.randint(0, COLUMNS-1)
                        tuple_loc = (row_x, column_x)
                        if(tuple_loc not in list_of_locs):
                            # print("appending...", tuple_loc)
                            list_of_locs.append(tuple_loc)
                        elif(tuple_loc in list_of_locs):
                            print("following duble item detected:", tuple_loc, "and prevented to have double.")
                    # print(list_of_locs)
                    
                    
                    
                    for i in range(len(list_of_locs)):
                        # print(i)
                        row = list_of_locs[i][0]
                        column = list_of_locs[i][1]
                        grid[row][column].agent = True
                        grid[row][column].agent_id = i
                        # create random colors and assign these colors to each agent
                        col = random_color()
                        colors.append(col)
                        agent_list[i] = agent(row,column)
                        agent_list[i].agent_id = i
                        agent_locs[(agent_list[i].row,agent_list[i].column)] = agent_list[i].agent_id
                        # current_matrix_state()
                        print("Agent",i,"'s energy is:", agent_list[i].start_energy)

                # if event.key == pygame.K_b:
                #     pygame.image.save(screen, "start.jpg")
                
                if event.key == pygame.K_n:
                    # start = time.time()
                    # step_counter = 0
                    # pygame.image.save(screen, "start.png")
                    
                    # while step_counter < 500:
                    #     empty_dic_counter = 0
                        # for i in range(index+1):
                    
                        # index keeps the number of agents (ex: index is 1(0 and 1) when 2 agent is selected)
                    for i in range(index+1):
                    # for i in range(len(list_of_locs)):
                        # print("Agent", i, "th location is:", agent_list[i].row, agent_list[i].column, "Now adding this agent's neighbours into coming_set...")
                        # print("Agent", i, "th neigbors are:", neighbours(agent_list[i].row, agent_list[i].column))
                        neighbor_list = find_neighbours(agent_list[i].row, agent_list[i].column)
                        # print("###Full neighbor cells before subtracting the agent locs for agent",i,": ",neighbor_list)
                        # DELETE - why we have this?
                        # grid[agent_list[i].row][agent_list[i].column].agent_id = i

                        agent_list[i].calc_neighbor_distance(neighbor_list)
                        # print("###agent_list[i].neighbors",agent_list[i].neighbors)
                        agent_list[i].movable_cells(agent_locs)
                        # print("current movable cells for the agent", agent_list[i].neighbors)


                            # update neighbors with the movable cells instead
                            # print("###agent_list[i].neighbors",agent_list[i].neighbors)
                            # print("Movable options for agent",i,"is:",agent_list[i].neighbors)
                            # # check if there is a place to move in movable neighbors
                            # # if there is no place to move, then send bids to all other not visited cells
                        # each agent submit their bids to its movable neighbors
                        
                        if(agent_list[i].start_energy > 0):
                            # chose one of the neighbor of the agent and add it into agent_locs
                            # so that it cannot be selected with another agent on the further iterations
                            
                            neighbors_for_agent = list(agent_list[i].neighbors.items())
                            # print("Here are the neighbors for the agent",i,":::",neighbors_for_agent)
                            if(len(neighbors_for_agent)>0):
                                key, val = random.choice(neighbors_for_agent)
                                # print("The random pair for the agent:", agent_list[i].agent_id, "is:",key, val[0])
                                agent_locs[key] = i
                                distance_of_move = agent_list[i].calc_won_distance(key[0], key[1])
                                # print("Currently the agent",i,"is at:", agent_list[i].row, agent_list[i].column)
                                # print("And now it will move to its new randomly selected location which is:", key[0], key[1])
                                print("Distance that the agent", i, "will move is:", distance_of_move)
                                if(agent_list[i].start_energy >= (distance_of_move + 5)):
                                    grid[key[0]][key[1]].agent_id = i
                                    grid[key[0]][key[1]].agent = True
                                    agent_list[i].row = key[0]
                                    agent_list[i].column = key[1]
                                    print("Now the agent is at:", agent_list[i].row, agent_list[i].column)
                                    # # update the agent locs after we move the agents to new locs
                                    agent_locs[(agent_list[i].row,agent_list[i].column)] = agent_list[i].agent_id
                                    print("agent locs current state is:", agent_locs)
                            else:
                                print("Uh Oh. The agent", i, "cannot move since there is no place to move right now.")
                                # the agent should pick a cell from far
                                # should it pick the closest or a random cell?
                                # CLOSEST approach is picked same as the bidding approach
                                visited_cells = bring_all_visited_locations()
                                # print("For agent",agent_list[i].agent_id,"located at", agent_list[i].row, agent_list[i].column, "here are the all visited cells:", visited_cells)
                                agent_list[i].distance_matrix = agent_list[i].calc_distance_matrices()
                                for x in visited_cells:
                                    row_c,column_c = x[0],x[1]
                                    # print(row_c,column_c)
                                    agent_list[i].distance_matrix[row_c][column_c] = None  
                                # print("agent_list[i].distance_matrix", agent_list[i].distance_matrix)
                                min_value_among_unv_cells = np.unravel_index(np.nanargmin(agent_list[i].distance_matrix, axis=None), agent_list[i].distance_matrix.shape)
                                # print("Min value for the distance matrix", np.nanargmin(agent_list[i].distance_matrix), "at location", min_value_among_unv_cells)
                                # print("min_value_among_unv_cells",min_value_among_unv_cells)

                                grid[min_value_among_unv_cells[0]][min_value_among_unv_cells[1]].agent_id = i
                                grid[min_value_among_unv_cells[0]][min_value_among_unv_cells[1]].agent = True
                                
                                agent_list[i].row = min_value_among_unv_cells[0]
                                agent_list[i].column = min_value_among_unv_cells[1]
                                print("Now the agent is at:", agent_list[i].row, agent_list[i].column)
                                agent_locs[min_value_among_unv_cells] = i

                                # mark the visited cell locations as "None" since we are interested in to find lowest cost unvisited cell

                                
                                #     row_c,column_c = i[0],i[1]
                                #     agent_list[i].distance_matrix[row_c][column_c] = None
                        
                                # # print("self.distance_matrix", self.distance_matrix)
                                # # if the distance matrix if full of "nan" values, then "all_areas_explored" flag will turn to TRUE
                                # if(np.isnan(agent_list[i].distance_matrix).all()):
                                #     # print("YESSS")
                                #     all_areas_explored = True
                                #     break

                            
                            
                            
                            

                        # else:
                        #     print("You are negative. You cannot bid.")
                            # agent_list[i].zero_bid()
                        # print("*****AGENT BID OFFERS FOR EACH NEIGHBOR CELLS*****")
                        # for i in agent_list:
                        #     print("Agent",i,"bids:", agent_list[i].neighbors)

                        

                    #     # for each neighbor cell: list the bids
                    #     # ex: for (1,1) cells which agents offered a bid and which amount
                    #     # put all these "agent_list[i].neighbors" into one dictionary with their agent IDs
                        
                    #     for i in agent_list:
                    #         # print("agent_list[i].neighbors",agent_list[i].neighbors)
                    #         for j in range(len(agent_list[i].neighbors)):
                    #             # print("Agent",i,"keys:", j)                               # list the numbers
                    #             # print("keys", list(agent_list[i].neighbors.keys())[j])
                    #             coming_list_element = list(agent_list[i].neighbors.values())[j]
                    #             coming_list_element.append(i)
                    #             try:
                    #                 all_bids[list(agent_list[i].neighbors.keys())[j]].append(coming_list_element)
                    #             except:
                    #                 all_bids[list(agent_list[i].neighbors.keys())[j]] = [coming_list_element]
                    #     # print("ALLLLLLLL",all_bids)
                    #     # print("ALL KEYS", all_bids.keys())
                    #     # print("ALL VALUES", all_bids.values())
                    #     for x in all_bids:
                    #         # print("for the cells", x, "the bids are as follows:", all_bids[x])
                    #         a = np.array(all_bids[x])
                    #         highestbid = a.max(axis=0)[1]
                    #         # print("here is the highest_bid", highestbid)
                    #         highestbid_index = a.argmax(axis=0)[1]
                    #         # among the neighbor cells, assign one cell at a time to the highest bidder
                    #         # which agent win which cells?
                    #         # print("the cell", x, "is won with max bid", highestbid, "by the agent:",all_bids[x][highestbid_index][2])
                    #         # now the agent either will go to cell that it sent a higher bid
                    #         # list the won cells for each agent
                    #         if(highestbid>0.0):
                    #             agent_list[all_bids[x][highestbid_index][2]].win_cells[x] = highestbid
                    #     # for i in agent_list:
                    #     #     print("Agent",i,"win cells with their bids:", agent_list[i].win_cells)

                    #     agent_locs.clear()
                        
                    #     for i in agent_list:
                    #         if agent_list[i].win_cells:
                    #             # print("\n\n******1here")
                    #             max_item_value = max(agent_list[i].win_cells.values())
                    #             tup = [k for k, v in agent_list[i].win_cells.items() if v == max_item_value]
                    #             # print(len(tup))
                    #             if len(tup) > 1:
                    #                 ll = random.choice(tup)
                    #                 row_val, column_val = ll
                    #                 # print(ll)

                    #             else:
                    #                 # print(tup[0])
                    #                 row_val, column_val = tup[0]
                                
                    #             # row_val, column_val = tup
                    #             # print("&&&&&&&&&&&&")
                    #             # print("where is the agent currently:", agent_list[i].row, agent_list[i].column)
                    #             distance_of_move = agent_list[i].calc_won_distance(row_val, column_val)

                    #             # print("hurr1", (distance_of_move + 5))
                    #             # print("hurr2", agent_list[i].start_energy)

                    #             if(agent_list[i].start_energy >= (distance_of_move + 5)):
                    #                 grid[row_val][column_val].agent_id = i
                    #                 grid[row_val][column_val].agent = True
                    #                 agent_list[i].row = row_val
                    #                 agent_list[i].column = column_val
                    #                 # update the agent locs after we move the agents to new locs
                    #                 agent_locs[(agent_list[i].row,agent_list[i].column)] = agent_list[i].agent_id


                    #                 # print("how are the win_cells now for agent", i,":::",agent_list[i].win_cells)
                    #                 # print("the cell that the agent moves is:", row_val, column_val)
                                    
                    #                 # agent_list[i].start_energy = agent_list[i].start_energy - (distance_to_win_cell + cleaning_value)
                    #                 agent_list[i].start_energy = agent_list[i].start_energy - (distance_of_move + 5)
                    #                 # print("new energy value for agent", i, "after the visitation:", agent_list[i].start_energy)
                    #             else:
                    #                 agent_locs[(agent_list[i].row,agent_list[i].column)] = agent_list[i].agent_id
                    #                 agent_list[i].start_energy = 0

                    #         else:
                    #             empty_dic_counter = empty_dic_counter + 1
                    #             # print("2here")
                    #             # print("dic is empty for agent",i)
                    #             # print(empty_dic_counter)
                    #             if(empty_dic_counter == index+1):
                    #                 # print("HELLO")
                    #                 all_dics_are_empty = True

                    #         # print("After the iteration, the energies are as follows for agent",i,":::",agent_list[i].start_energy)
                    #     # current_matrix_state()

                        
                        
                        
                    #     # print("****************************\n\nclearing...")
                    #     all_bids.clear()
                    #     for i in agent_list:
                    #         agent_list[i].win_cells.clear()

                    #     # print("huu")
                    #     # pygame.image.save(screen, "final.jpg")
                    #     if(all_areas_explored | all_dics_are_empty):
                    #         # which one is true
                    #         end = time.time()
                    #         print("all_areas_explored",all_areas_explored)
                    #         print("all_dics_are_empty",all_dics_are_empty)
                    #         # print("Testing2")
                    #         # pygame.image.save(screen, "final.png")
                    #         break
                    #         # pygame.quit()   # we are done so we exit this loop
                    #         # sys.exit()
                        
                    #     step_counter = step_counter+1
                    # # pygame.image.save(screen, "final.png")
                
                if event.key == pygame.K_t:
                    print(end - start)
                    pygame.image.save(screen, "final.png")


                


        # Set the screen background
        screen.fill(COLOR_BLACK)

        # Draw the grid
        for row in range(ROWS):
            for column in range(COLUMNS):
                
                box = grid[row][column]
                
                if grid[row][column].agent_id == None:
                    box.draw(screen, COLOR_GRAY)

                # problem
                # below parameter in range function should be assigned globally
                for i in range(100):
                    if grid[row][column].agent_id == i:
                        box.draw(screen, colors[i])

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

main()
