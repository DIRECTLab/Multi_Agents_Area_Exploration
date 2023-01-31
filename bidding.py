import pygame
import sys
import numpy as np
import time
import random

COLUMNS = 54
ROWS = 54
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
COLOR_BROWN = (139,69,19)

agent_list, agent_locs = dict(),dict()
wall_list = list()
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
        self.wall = False          # is the cell already visited or not visited (mark it as either False or True)
        
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
        self.start_energy = random.randint(50, 200)

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

    # each agent send bids to its neighbors in each iteration
    def send_bid(self):
        global all_areas_explored
        # If the agent only has one neighbor, offer a bid based on the neighbor is visited or not
        if(len(self.neighbors)==1):
            for key, value in self.neighbors.items():
                if(grid[key[0]][key[1]].agent == True):
                    # print("*** 111 ***")
                    self.neighbors[key].append(0)
                    # print("Agent",self.agent_id, "bids:", 0)
                else:
                    # print("*** 222 ***")
                    self.neighbors[key].append((1/self.start_energy) * (1 / (0.5 * value[0])))
                    # print("Agent",self.agent_id, "bids:", [(1/self.start_energy) * (1 / (0.5 * value[0]))])

        # If an agent has more than one neighbor, offer a bid for each neighbors based on the neighbors are visited or not
        else:
            # use the following count variable for the following purpose:
            # check one by one each neighbors, if the selected neighbor is previously visited, increase the counter
            # if all neighbors are previously visited, then that agent should send a bid to the most profitable unexplored cell
            count=0
            # copy the self.neighbors dictionary to prevent runtime error since we are adding new elements to the neighbors dictionary during the iteration
            neighbors_copy = tuple(self.neighbors.items())

            # for each neighbor of an agent, check their neighbors whether a neighbor is previosly visited or not
            for key, value in neighbors_copy:
                # print("Agent", self.agent_id, "has following neighbors:", self.neighbors)
                
                # if a neighbor is previosly visited, offer something less
                if(grid[key[0]][key[1]].agent == True):
                    # print("*** 333 ***")
                    self.neighbors[key].append(0)
                    # print("Agent",self.agent_id, "is going to offer for the neighbor",key[0],key[1],"with the bid:",0)
                    
                    # if all neighbors for the agent are previously visited or has an agent in one one of the neighbor locs, then bid to other cells that are not visited
                    count = count + 1
                    if(count == len(self.neighbors)):
                        # print("YEAP It worked for agent", self.agent_id, "with having all", count, "neighbors are previously visited!")
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
                        
                        # print("self.distance_matrix", self.distance_matrix)
                        # if the distance matrix if full of "nan" values, then "all_areas_explored" flag will turn to TRUE
                        if(np.isnan(self.distance_matrix).all()):
                            # print("YESSS")
                            all_areas_explored = True
                            break

                        
                        # print("Min value for the distance matrix", np.nanmin(self.distance_matrix), "at location", np.nanargmin(self.distance_matrix))
                        min_value_among_unv_cells = np.unravel_index(np.nanargmin(self.distance_matrix, axis=None), self.distance_matrix.shape)
                        # add the most valuable cell to the neighbor list of the agent
                        self.neighbors[min_value_among_unv_cells] = [np.nanmin(self.distance_matrix), ((1/self.start_energy) * ((1 / np.nanmin(self.distance_matrix)) + 1))]
                        # print("New neighbors for the agent",self.agent_id,"is as follows:", self.neighbors)
                        # print("*** 555 ***")
                        # print("Agent",self.agent_id, "is going to offer for the neighbor",np.nanmin(self.distance_matrix),"with the bid:",[(1/self.start_energy) *(((1 / np.nanmin(self.distance_matrix)) + 1))])
                # if the neighbor is previously not visited, then offer something higher
                elif(grid[key[0]][key[1]].agent == False):
                    # print("*** 444 ***")
                    self.neighbors[key].append((1/self.start_energy) * (1 / value[0]))
                    # print("Agent",self.agent_id, "is going to offer for the neighbor",key[0],key[1],"with the bid:",[(1/self.start_energy) * (1 / value[0])])
    # this function send a zero bid to a neighbor when it does not have an energy left
    def zero_bid(self):
        for key, value in self.neighbors.items():
            # print("*** 666 ***")
            self.neighbors[key].append(0)
            # print("Agent",self.agent_id, "bids:", 0, "since it does not have any enery left.")

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
        time.sleep(0.05)
        for event in pygame.event.get():  # User did something
            
        
            
            
            
            
            
            
            
            if event.type == pygame.QUIT:  # If user clicked close
                pygame.quit()   # we are done so we exit this loop
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if(event.button==1):
                    index = index + 1
                    pos = pygame.mouse.get_pos()
                    column = pos[0] // (CELL_WIDTH + MARGIN)
                    row = pos[1] // (CELL_HEIGHT + MARGIN)
                    grid[row][column].agent = True
                    grid[row][column].agent_id = index
                    col = random_color()
                    colors.append(col)
                    agent_list[index] = agent(row,column)
                    agent_list[index].agent_id = index
                    agent_locs[(agent_list[index].row,agent_list[index].column)] = agent_list[index].agent_id
                    current_matrix_state()
                    print("Agent",index,"'s energy is:", agent_list[index].start_energy)

            elif event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                column = pos[0] // (CELL_WIDTH + MARGIN)
                row = pos[1] // (CELL_HEIGHT + MARGIN)
                if event.buttons[2]:
                    grid[row][column].wall = True
                    # if((row,column) not in wall_list):
                    #     wall_list.append((row,column))
                    # print(wall_list)
                
                    



            if event.type == pygame.KEYDOWN:
                
                
                
                if event.key == pygame.K_a:
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
                    start = time.time()
                    step_counter = 0
                    # pygame.image.save(screen, "start.png")
                    
                    while step_counter < 500:
                        empty_dic_counter = 0
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
                            # update neighbors with the movable cells instead
                            # print("###agent_list[i].neighbors",agent_list[i].neighbors)
                            # print("Movable options for agent",i,"is:",agent_list[i].neighbors)
                            # # check if there is a place to move in movable neighbors
                            # # if there is no place to move, then send bids to all other not visited cells
                        # each agent submit their bids to its movable neighbors
                        for i in agent_list:
                            if(agent_list[i].start_energy > 0):
                                agent_list[i].send_bid()
                            else:
                                # print("You are negative. You cannot bid.")
                                agent_list[i].zero_bid()
                        # print("*****AGENT BID OFFERS FOR EACH NEIGHBOR CELLS*****")
                        # for i in agent_list:
                        #     print("Agent",i,"bids:", agent_list[i].neighbors)

                        

                        # for each neighbor cell: list the bids
                        # ex: for (1,1) cells which agents offered a bid and which amount
                        # put all these "agent_list[i].neighbors" into one dictionary with their agent IDs
                        
                        for i in agent_list:
                            # print("agent_list[i].neighbors",agent_list[i].neighbors)
                            for j in range(len(agent_list[i].neighbors)):
                                # print("Agent",i,"keys:", j)                               # list the numbers
                                # print("keys", list(agent_list[i].neighbors.keys())[j])
                                coming_list_element = list(agent_list[i].neighbors.values())[j]
                                coming_list_element.append(i)
                                try:
                                    all_bids[list(agent_list[i].neighbors.keys())[j]].append(coming_list_element)
                                except:
                                    all_bids[list(agent_list[i].neighbors.keys())[j]] = [coming_list_element]
                        # print("ALLLLLLLL",all_bids)
                        # print("ALL KEYS", all_bids.keys())
                        # print("ALL VALUES", all_bids.values())
                        for x in all_bids:
                            # print("for the cells", x, "the bids are as follows:", all_bids[x])
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
                        
                        for i in agent_list:
                            if agent_list[i].win_cells:
                                # print("\n\n******1here")
                                max_item_value = max(agent_list[i].win_cells.values())
                                tup = [k for k, v in agent_list[i].win_cells.items() if v == max_item_value]
                                # print(len(tup))
                                if len(tup) > 1:
                                    ll = random.choice(tup)
                                    row_val, column_val = ll
                                    # print(ll)

                                else:
                                    # print(tup[0])
                                    row_val, column_val = tup[0]
                                
                                # row_val, column_val = tup
                                # print("&&&&&&&&&&&&")
                                # print("where is the agent currently:", agent_list[i].row, agent_list[i].column)
                                distance_of_move = agent_list[i].calc_won_distance(row_val, column_val)

                                # print("hurr1", (distance_of_move + 5))
                                # print("hurr2", agent_list[i].start_energy)

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

                            else:
                                empty_dic_counter = empty_dic_counter + 1
                                # print("2here")
                                # print("dic is empty for agent",i)
                                # print(empty_dic_counter)
                                if(empty_dic_counter == index+1):
                                    # print("HELLO")
                                    all_dics_are_empty = True

                            # print("After the iteration, the energies are as follows for agent",i,":::",agent_list[i].start_energy)
                        # current_matrix_state()

                        
                        
                        
                        # print("****************************\n\nclearing...")
                        all_bids.clear()
                        for i in agent_list:
                            agent_list[i].win_cells.clear()

                        # print("huu")
                        # pygame.image.save(screen, "final.jpg")
                        if(all_areas_explored | all_dics_are_empty):
                            # which one is true
                            end = time.time()
                            print("all_areas_explored",all_areas_explored)
                            print("all_dics_are_empty",all_dics_are_empty)
                            # print("Testing2")
                            # pygame.image.save(screen, "final.png")
                            break
                            # pygame.quit()   # we are done so we exit this loop
                            # sys.exit()
                        
                        step_counter = step_counter+1
                    # pygame.image.save(screen, "final.png")
                
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
                    box.draw(screen, COLOR_WHITE)
                
                if grid[row][column].wall == True:
                    box.draw(screen, COLOR_BROWN)

                # problem
                # below parameter in range function should be assigned globally
                for i in range(100):
                    if grid[row][column].agent_id == i:
                        box.draw(screen, colors[i])

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

main()
