import random
import numpy as np
import numpy as np
import random
import math
from itertools import product, starmap, islice

def get_random_point(ground_truth_map, cfg):
    index_list = list(np.argwhere(ground_truth_map == cfg.EMPTY))
    random.shuffle(index_list)
    point_xy = (index_list[0][1], index_list[0][0])
    return point_xy


def get_closest_point_rc(pointlist, grid_position_xy):
    min_dist = np.inf
    min_point = None
    for point_rc in pointlist:
        dist = np.sqrt((point_rc[1] - grid_position_xy[0])**2 + (point_rc[0] - grid_position_xy[1])**2)
        if dist < min_dist:
            min_dist = dist
            min_point = point_rc
    if min_point is None:
        raise Exception("min_point is None")
    return min_point


def get_new_location_xy(map_area, MapLocationType, useRandom=False, closest_point_to_xy=None):
        if useRandom and closest_point_to_xy is not None:
            raise Exception("useRandom and point_xy are mutually exclusive")
        
        if MapLocationType ==None:
            raise Exception("MapLocationType is None set it to self.cfg.FRONTIER or self.cfg.UNKNOWN")
        if len(map_area) == 0:
            return None
        
        if map_area[0].shape == (2,):
            points_array = map_area 
        else:
            points_array = np.argwhere(map_area == MapLocationType)
        
        if len(points_array) == 0:
            return None
        elif len(points_array) == 1:
            return (points_array[0][1], points_array[0][0])
        
        if useRandom:
            # choose a random point
            idx = np.random.randint(len(points_array))
            return (points_array[idx][1], points_array[idx][0])

        point = get_closest_point_rc(list(points_array), closest_point_to_xy)
        return (point[1], point[0])




def points_over_radious(rows, cols, n, location_of_radious, start_angle=0, end_angle=2*np.pi):
    radius = math.ceil(cols * 0.1)
    if location_of_radious == 'center':
        location_of_radious_point = (int(cols/2), int(rows/2))
    elif location_of_radious == 'topleft':
        location_of_radious_point = (1, 1)
        radius +=6
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
# def findNeighbors(grid, x, y, level):
#     if level == 1:
#         xi = (0, -level, level) if 0 < x < len(grid) - 1 else ((0, -level) if x > 0 else (0, level))
#         yi = (0, -level, level) if 0 < y < len(grid[0]) - 1 else ((0, -level) if y > 0 else (0, level))
#         return islice(starmap((lambda a, b: (x + a, y + b)), product(xi, yi)), 1, None)
#     elif level == 2:
#         xi = (0, -level, -(level-1), (level-1), level) if 0 < x < len(grid) - 1 else ((0, -(level-1), -level) if x > 0 else (0, (level-1), level))
#         yi = (0, -level, -(level-1), (level-1), level) if 0 < y < len(grid[0]) - 1 else ((0, -(level-1), -level) if y > 0 else (0, (level-1), level))
#         return islice(starmap((lambda a, b: (x + a, y + b)), product(xi, yi)), 1, None)
from itertools import product, islice, starmap

def findNeighbors(grid, x, y, level):
    xi_range = range(-level, level+1)
    yi_range = range(-level, level+1)
    
    if 0 <= x < len(grid) and 0 <= y < len(grid[0]):
        xi = xi_range if 0 < x < len(grid) - 1 else (xi_range[:-1] if x > 0 else xi_range[1:])
        yi = yi_range if 0 < y < len(grid[0]) - 1 else (yi_range[:-1] if y > 0 else yi_range[1:])
        return islice(starmap((lambda a, b: (x + a, y + b)), product(xi, yi)), 1, None)
    else:
        return []


# class Point_Finding:
#     def get_random_point(self):
#         index_list = list(np.argwhere(self.ground_truth_map == self.cfg.EMPTY))
#         # shuffle the list
#         random.shuffle(index_list,)
#         # get the first point
#         point_xy = (index_list[0][1], index_list[0][0])
#         return point_xy

    
#     def get_closest_point_rc(self, pointlist):
#         '''
#         This function returns the closest point from the pointlist to the agent
#         :param pointlist: a list of points (r,c)
#         :return: the closest point from the pointlist to the agent
#         '''
#         min_dist = np.inf
#         min_point = None
#         for point_rc in pointlist:
#             dist = np.sqrt((point_rc[1] - self.grid_position_xy[0])**2 + (point_rc[0] - self.grid_position_xy[1])**2)
#             if dist < min_dist:
#                 min_dist = dist
#                 min_point = point_rc
#         if min_point is None:
#             raise Exception("min_point is None")
#         return min_point
    
#     def get_new_location_xy(self,map_area,  MapLocationType = None, useRandom = False):
#         '''
#         This function returns a random location from the map_area
#         :param map_area: the map area to choose from typically self.agent_map
#         :param MapLocationType: the type of location to choose from: self.cfg.FRONTIER or self.cfg.UNKNOWN
#         :return: a random location from the map_area (x,y) or None if no location is found
#         '''
#         if MapLocationType ==None:
#             raise Exception("MapLocationType is None set it to self.cfg.FRONTIER or self.cfg.UNKNOWN")
#         if len(map_area) == 0:
#             return None
        
#         if map_area[0].shape == (2,):
#             points_array = map_area 
#         else:
#             points_array = np.argwhere(map_area == MapLocationType)
        
#         if len(points_array) == 0:
#             return None
#         elif len(points_array) == 1:
#             return (points_array[0][1], points_array[0][0])
        
#         if useRandom:
#             # choose a random point
#             idx = np.random.randint(len(points_array))
#             return (points_array[idx][1], points_array[idx][0])

#         point = get_closest_point_rc(list(points_array))
#         return (point[1], point[0])
    