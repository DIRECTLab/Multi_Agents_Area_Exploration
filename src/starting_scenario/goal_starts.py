import numpy as np
import math
from itertools import product, starmap, islice

#  will make sure we have different random points over grid for goal positions
OTHER_AGENT_LOCATIONS_GOAL = []

class Base_Start:
    def check_if_valid_point(self, ground_truth_map, cfg):
  
        # checking level 1 neighbors
        neighbors = list(findNeighbors(ground_truth_map, self.goal_xy[0], self.goal_xy[1], 1))
        for cur_point in neighbors:

            if cur_point[0] < 0 or cur_point[0] >= self.cfg.COLS or cur_point[1] < 0 or cur_point[1] >= self.cfg.ROWS:
                # shift the point to be in the map
                self.goal_xy = (max(1, min(cur_point, self.cfg.COLS-2)), max(1, min(cur_point[1], self.cfg.ROWS-2)))
                return True
            # check if the point is not on an obstacle
            if (self.ground_truth_map[cur_point[1], cur_point[0]] == self.cfg.OBSTACLE):
                continue
            if cur_point in OTHER_AGENT_LOCATIONS_GOAL:
                continue
            if ground_truth_map[cur_point[1], cur_point[0]] == cfg.EMPTY:
                # point = cur_point
                self.goal_xy =cur_point
                return True
        
        # checking level 2 neighbors
        neighbors = list(findNeighbors(ground_truth_map, self.goal_xy[0], self.goal_xy[1], 2))
        for cur_point in neighbors:
            if cur_point in OTHER_AGENT_LOCATIONS_GOAL:
                continue
            if ground_truth_map[cur_point[1], cur_point[0]] == cfg.EMPTY:
                self.goal_xy  = cur_point
                return True
        
        print("WARNING: All the neighbors are obstacles or off the map!! Here are the neighbors: ", neighbors)
        return False

class Manual_Goal:
    four_goal_pos = [(10,10), (20,20), (30,30), (45,45)]
    def choose_start_goal(self):
        self.goal_xy = self.four_goal_pos[self.id]

class Rand_Start_Goal:
    def choose_start_goal(self):
        self.goal_xy = self.get_random_point()
        if self.goal_xy not in OTHER_AGENT_LOCATIONS_GOAL:
            OTHER_AGENT_LOCATIONS_GOAL.append(self.goal_xy)
        else:
            self.goal_xy = self.get_random_point()
            OTHER_AGENT_LOCATIONS_GOAL.append(self.goal_xy)

class Center_Start_Goal(Base_Start):
    def choose_start_goal(self):

        self.goal_xy = points_over_radious(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS, 'center')[self.id]
        self.goal_xy = (int(np.round(self.goal_xy[0])), int(np.round(self.goal_xy[1])))
        OTHER_AGENT_LOCATIONS_GOAL.append(self.goal_xy)
        
        found_goal = self.check_if_valid_point(self.ground_truth_map, self.cfg)
        if not found_goal:
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.goal_xy)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.goal_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.goal_xy)
            return
        
class Top_Left_Start_Goal(Base_Start):
    def choose_start_goal(self):

        self.goal_xy = points_over_radious(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS, 'topleft')[self.id]
        self.goal_xy = (int(np.round(self.goal_xy[0])), int(np.round(self.goal_xy[1])))
        OTHER_AGENT_LOCATIONS_GOAL.append(self.goal_xy)
        
        found_goal = self.check_if_valid_point(self.ground_truth_map, self.cfg)
        if not found_goal:
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.goal_xy)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.goal_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.goal_xy)
            return

class Edge_Start_Goal(Base_Start):
    def choose_start_goal(self):
        
        self.goal_xy = points_on_rectangle_edge(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS)[self.id]
        self.goal_xy = (int(np.round(self.goal_xy[0])), int(np.round(self.goal_xy[1])))
        OTHER_AGENT_LOCATIONS_GOAL.append(self.goal_xy)
        
        found_goal = self.check_if_valid_point(self.ground_truth_map, self.cfg)
        if not found_goal:
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.goal_xy)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.goal_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.goal_xy)
            return

class Distributed_Goal(Base_Start):
    def choose_start_goal(self):
        self.goal_xy = dividegrid(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS)[self.id]
        self.goal_xy = (int(np.round(self.goal_xy[0])), int(np.round(self.goal_xy[1])))
        OTHER_AGENT_LOCATIONS_GOAL.append(self.goal_xy)
        
        found_goal = self.check_if_valid_point(self.ground_truth_map, self.cfg)
        if not found_goal:
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.goal_xy,)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.goal_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.goal_xy)
            return








def points_over_radious(rows, cols, n, location_of_radious, start_angle=0, end_angle=2*np.pi):
    radius = math.ceil(cols * 0.1)
    if location_of_radious == 'center':
        location_of_radious_point = (int(cols/2), int(rows/2))
    elif location_of_radious == 'topleft':
        location_of_radious_point = (1, 1)
        radius +=2
        end_angle = np.pi/2
    
    # Initialize an empty array to hold the coordinates of each point
    points = np.zeros((n, 2))
    # Calculate the angle between each point on the perimeter
    angles = np.linspace(start_angle, end_angle, n, endpoint=False) #0, 2*np.pi, n, endpoint=False)
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
    if len(y)<2 and y[0] == 0:
        y[0] = rows/2

    x_var = []
    y_var = []

    for i in x:
        for j in y:
            x_var.append(i)
            y_var.append(j)
    
    # x_offset and y_offset are used to shift the points to the center of the grid
    for i in x_var:
        if i != 0:
            x_offset = i/2
            break
    y_offset = (y_var[1] - y_var[0]) / 2

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
