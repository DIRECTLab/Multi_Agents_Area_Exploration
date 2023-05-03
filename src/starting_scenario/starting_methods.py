import numpy as np
import random
import math
from itertools import product, starmap, islice

#  will make sure we have different random points over grid for agent positions
CHECK_RAND_LIST_START = []

class Manual_Start:
    four_start_pos = [(2, 7), (9, 16), (2, 5), (3, 11)]
    def choose_start_position(self):
        self.grid_position_xy = self.four_start_pos[self.id]

class Rand_Start_Position:
    def __init__(self):
        print("hello from random start")
        # random.seed(cfg.SEED)
    def choose_start_position(self):
        self.grid_position_xy = self.get_random_point()
        if self.grid_position_xy not in CHECK_RAND_LIST_START:
            CHECK_RAND_LIST_START.append(self.grid_position_xy)
            # print("CHECK_RAND_LIST_START length:::", len(CHECK_RAND_LIST_START))
        else:
            self.grid_position_xy = self.get_random_point()
            CHECK_RAND_LIST_START.append(self.grid_position_xy)
            # print("CHECK_RAND_LIST_START length:::", len(CHECK_RAND_LIST_START))

class Center_Start_Position:
    def choose_start_position(self):
        self.grid_position_xy = points_over_radious(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS, 'center')[self.id]
        
        self.grid_position_xy = (int(np.round(self.grid_position_xy[0])), \
                                int(np.round(self.grid_position_xy[1])))
        
        find_new_point = False
        # check if the point is in the map
        if self.grid_position_xy[0] < 0 or self.grid_position_xy[0] >= self.cfg.COLS or \
            self.grid_position_xy[1] < 0 or self.grid_position_xy[1] >= self.cfg.ROWS:
            find_new_point = True
            # shift the point to be in the map
            self.grid_position_xy = (max(1, min(self.grid_position_xy[0], self.cfg.COLS-2)), \
                                    max(1, min(self.grid_position_xy[1], self.cfg.ROWS-2)))
        # check if the point is not on an obstacle
        elif self.ground_truth_map[self.grid_position_xy[1], self.grid_position_xy[0]] == self.cfg.OBSTACLE:
            find_new_point = True

        if find_new_point:
            foundPoint  = check_if_valid_point(self.grid_position_xy, self.ground_truth_map, self.cfg)
            if foundPoint[0]:
                self.goal_xy = foundPoint[1]
                return
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.grid_position_xy)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.grid_position_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.grid_position_xy)
            return

class Top_Left_Start_Position:
    def choose_start_position(self):
        self.grid_position_xy = points_over_radious(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS, 'topleft')[self.id]
        
        self.grid_position_xy = (int(np.round(self.grid_position_xy[0])), \
                                int(np.round(self.grid_position_xy[1])))
        
        find_new_point = False
        # check if the point is in the map
        if self.grid_position_xy[0] < 0 or self.grid_position_xy[0] >= self.cfg.COLS or \
            self.grid_position_xy[1] < 0 or self.grid_position_xy[1] >= self.cfg.ROWS:
            find_new_point = True
            # shift the point to be in the map
            self.grid_position_xy = (max(1, min(self.grid_position_xy[0], self.cfg.COLS-2)), \
                                    max(1, min(self.grid_position_xy[1], self.cfg.ROWS-2)))
        # check if the point is not on an obstacle
        elif self.ground_truth_map[self.grid_position_xy[1], self.grid_position_xy[0]] == self.cfg.OBSTACLE:
            find_new_point = True

        if find_new_point:
            foundPoint  = check_if_valid_point(self.grid_position_xy, self.ground_truth_map, self.cfg)
            if foundPoint[0]:
                self.goal_xy = foundPoint[1]
                return
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.grid_position_xy)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.grid_position_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.grid_position_xy)
            return

class Edge_Start_Position:
    def choose_start_position(self):
        self.grid_position_xy = points_on_rectangle_edge(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS)[self.id]
        self.grid_position_xy = (int(np.round(self.grid_position_xy[0])), \
                                int(np.round(self.grid_position_xy[1])))
        
        find_new_point = False
        # check if the point is in the map
        if self.grid_position_xy[0] < 0 or self.grid_position_xy[0] >= self.cfg.COLS or \
            self.grid_position_xy[1] < 0 or self.grid_position_xy[1] >= self.cfg.ROWS:
            find_new_point = True
            # shift the point to be in the map
            self.grid_position_xy = (max(1, min(self.grid_position_xy[0], self.cfg.COLS-2)), \
                                    max(1, min(self.grid_position_xy[1], self.cfg.ROWS-2)))
        # check if the point is not on an obstacle
        elif self.ground_truth_map[self.grid_position_xy[1], self.grid_position_xy[0]] == self.cfg.OBSTACLE:
            find_new_point = True

        if find_new_point:
            foundPoint  = check_if_valid_point(self.grid_position_xy, self.ground_truth_map, self.cfg)
            if foundPoint[0]:
                self.goal_xy = foundPoint[1]
                return
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.grid_position_xy)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.grid_position_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.grid_position_xy)
            return

class Distributed_Start:
    def choose_start_position(self):
        self.grid_position_xy = dividegrid(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS)[self.id]
        
        find_new_point = False
        # check if the point is in the map
        if self.grid_position_xy[0] < 0 or self.grid_position_xy[0] >= self.cfg.COLS or \
            self.grid_position_xy[1] < 0 or self.grid_position_xy[1] >= self.cfg.ROWS:
            find_new_point = True
            # shift the point to be in the map
            self.grid_position_xy = (max(1, min(self.grid_position_xy[0], self.cfg.COLS-2)), \
                                    max(1, min(self.grid_position_xy[1], self.cfg.ROWS-2)))
        # check if the point is not on an obstacle
        elif self.ground_truth_map[self.grid_position_xy[1], self.grid_position_xy[0]] == self.cfg.OBSTACLE:
            find_new_point = True

        if find_new_point:
            foundPoint  = check_if_valid_point(self.grid_position_xy, self.ground_truth_map, self.cfg)
            if foundPoint[0]:
                self.goal_xy = foundPoint[1]
                return
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.grid_position_xy,)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.grid_position_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.grid_position_xy)
            return
            
def points_over_radious(rows, cols, n, location_of_radious):
    radius = math.ceil(cols * 0.1)
    if location_of_radious == 'center':
        location_of_radious_point = (int(cols/2), int(rows/2))
    elif location_of_radious == 'topleft':
        location_of_radious_point = (5, 5)
    
    # Initialize an empty array to hold the coordinates of each point
    points = np.zeros((n, 2))
    # Calculate the angle between each point on the perimeter
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    # Generate the coordinates of each point based on the angle from the center
    for i, angle in enumerate(angles):
        x = location_of_radious_point[0] + radius * np.cos(angle)
        y = location_of_radious_point[1] + radius * np.sin(angle)
        # Shift the point to be within the rectangle
        shift =1
        # Project the point onto the perimeter of the rectangle
        if x < 0:
            x = 0
            # y = center[1] - radius * np.sin(angle)
        if x >= cols:
            x = cols-shift
            # y = center[1] + radius * np.sin(angle)
        if y < 0:
            y = 0
            # x = center[0] - radius * np.cos(angle)
        if y >= rows:
            y = rows-shift
            # x = center[0] + radius * np.cos(angle)
        points[i, 0] = x
        points[i, 1] = y
    return points

def points_on_rectangle_edge(rows, cols, n):
    # Calculate the center of the rectangle
    center = np.array([cols / 2, rows / 2])
    # Calculate the radius of the rectangle
    radius = np.sqrt(cols**2 + rows**2) / 2
    # Initialize an empty array to hold the coordinates of each point
    points = np.zeros((n, 2))
    # Calculate the angle between each point on the perimeter
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    # Generate the coordinates of each point based on the angle from the center
    for i, angle in enumerate(angles):
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        # Shift the point to be within the rectangle
        shift =1
        # Project the point onto the perimeter of the rectangle
        if x < 0:
            x = 0
            # y = center[1] - radius * np.sin(angle)
        if x >= cols:
            x = cols-shift
            # y = center[1] + radius * np.sin(angle)
        if y < 0:
            y = 0
            # x = center[0] - radius * np.cos(angle)
        if y >= rows:
            y = rows-shift
            # x = center[0] + radius * np.cos(angle)
        points[i, 0] = x
        points[i, 1] = y
    return points

def check_if_valid_point(point, ground_truth_map, cfg):
    # checking level 1 neighbors
    neighbors = list(findNeighbors(ground_truth_map, point[0], point[1], 1))
    for cur_point in neighbors:
        if ground_truth_map[cur_point[1], cur_point[0]] == cfg.EMPTY:
            point = cur_point
            return [True, point]
    
    # checking level 2 neighbors
    neighbors = list(findNeighbors(ground_truth_map, point[0], point[1], 2))
    for cur_point in neighbors:
        if ground_truth_map[cur_point[1], cur_point[0]] == cfg.EMPTY:
            point = cur_point
            return [True, point]
    
    print("WARNING: All the neighbors are obstacles or off the map!! Here are the neighbors: ", neighbors)
    return False

def calc_closest_factors(c: int):
    if c//1 != c:
        raise TypeError("c must be an integer.")
    a, b, i = 1, c, 0
    while a < b:
        i += 1
        if c % i == 0:
            a = i
            b = c//a
        if i > 100:
            break
    return [b, a]

def dividegrid(rows, cols, n):
    agent_count = n
    turned_list = calc_closest_factors(int(agent_count))
    agentrowcount = turned_list[0]
    agentcolumncount = turned_list[1]
    
    x = np.arange(0, cols, cols/agentcolumncount)
    y = np.arange(0, rows, rows/agentrowcount)
    if y[0] == 0:
        y[0] = rows/2
    x_var = []
    y_var = []
    for i in x:
        for j in y:
            x_var.append(i)
            y_var.append(j)
    x_offset = (x_var[1] - x_var[0])/2
    y_offset = (y_var[1] - y_var[0])/2
    x_var = [int(x + x_offset) for x in x_var]
    y_var = [int(y + y_offset) for y in y_var]
    points = []
    for i in range(len(x_var)):
        points.append((x_var[i], y_var[i]))
    return points

# https://stackoverflow.com/questions/16245407/python-finding-neighbors-in-a-2-d-list
def findNeighbors(grid, x, y, level):
    if level == 1:
        xi = (0, -level, level) if 0 < x < len(grid) - 1 else ((0, -level) if x > 0 else (0, level))
        yi = (0, -level, level) if 0 < y < len(grid[0]) - 1 else ((0, -level) if y > 0 else (0, level))
        return islice(starmap((lambda a, b: (x + a, y + b)), product(xi, yi)), 1, None)
    elif level == 2:
        xi = (0, -level, -(level-1), (level-1), level) if 0 < x < len(grid) - 1 else ((0, -(level-1), -level) if x > 0 else (0, (level-1), level))
        yi = (0, -level, -(level-1), (level-1), level) if 0 < y < len(grid[0]) - 1 else ((0, -(level-1), -level) if y > 0 else (0, (level-1), level))
        return islice(starmap((lambda a, b: (x + a, y + b)), product(xi, yi)), 1, None)

# extended version of findNeighbors without itertools magic
# def findNeighbors_detailed_version(grid, x, y):
#     if 0 < x < len(grid) - 1:
#         xi = (0, -1, 1, -2, 2)   # this isn't first or last row, so we can look above and below
#     elif x > 0:
#         xi = (0, -1, -2)      # this is the last row, so we can only look above
#     else:
#         xi = (0, 1, 2)       # this is the first row, so we can only look below
#     # the following line accomplishes the same thing as the above code but for columns
#     yi = (0, -1, 1, -2, 2) if 0 < y < len(grid[0]) - 1 else ((0, -1, -2) if y > 0 else (0, 1, 2))
#     for a in xi:
#         for b in yi:
#             if a == b == 0:  # this value is skipped using islice in the original code
#                 continue
#             yield (x + a, y + b)
