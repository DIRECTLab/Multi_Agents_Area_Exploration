import numpy as np
import math
from itertools import product, starmap, islice

class Base_Start:
    def check_if_valid_point(self, point, ground_truth_map, cfg, other_agent_locations):
  
        # checking level 1 neighbors
        neighbors = list(self.findNeighbors(ground_truth_map, point[0], point[1], 1))
        for cur_point in neighbors:

            if cur_point[0] < 0 or cur_point[0] >= self.cfg.COLS or cur_point[1] < 0 or cur_point[1] >= self.cfg.ROWS:
                # shift the point to be in the map
                point = (max(1, min(cur_point, self.cfg.COLS-2)), max(1, min(cur_point[1], self.cfg.ROWS-2)))
                other_agent_locations.append(cur_point)
                return (True,cur_point)
            # check if the point is not on an obstacle
            if (self.ground_truth_map[cur_point[1], cur_point[0]] == self.cfg.OBSTACLE):
                continue
            if cur_point in other_agent_locations:
                continue
            if ground_truth_map[cur_point[1], cur_point[0]] == cfg.EMPTY:
                other_agent_locations.append(cur_point)
                print(other_agent_locations)
                return (True,cur_point)
        
        # checking level 2 neighbors
        print("WARNING: checking level 2 neighbors")
        neighbors = list(self.findNeighbors(ground_truth_map, point[0], point[1], 2))
        for cur_point in neighbors:
            if cur_point in other_agent_locations:
                continue
            if ground_truth_map[cur_point[1], cur_point[0]] == cfg.EMPTY:
                other_agent_locations.append(cur_point)
                return (True,cur_point)
        
        print("WARNING: All the neighbors are obstacles or off the map!! Here are the neighbors: ", neighbors)
        return False
    



    def points_over_radious(self, rows, cols, n, location_of_radious, start_angle=0, end_angle=2*np.pi):
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


    def points_on_rectangle_edge(self, rows, cols, n):
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


    def calc_closest_factors(self, c: int):
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

    def dividegrid(self, rows, cols, n):
        agent_count = n
        turned_list = self.calc_closest_factors(int(agent_count))
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
    def findNeighbors(self, grid, x, y, level):
        if level == 1:
            xi = (0, -level, level) if 0 < x < len(grid) - 1 else ((0, -level) if x > 0 else (0, level))
            yi = (0, -level, level) if 0 < y < len(grid[0]) - 1 else ((0, -level) if y > 0 else (0, level))
            return islice(starmap((lambda a, b: (x + a, y + b)), product(xi, yi)), 1, None)
        elif level == 2:
            xi = (0, -level, -(level-1), (level-1), level) if 0 < x < len(grid) - 1 else ((0, -(level-1), -level) if x > 0 else (0, (level-1), level))
            yi = (0, -level, -(level-1), (level-1), level) if 0 < y < len(grid[0]) - 1 else ((0, -(level-1), -level) if y > 0 else (0, (level-1), level))
            return islice(starmap((lambda a, b: (x + a, y + b)), product(xi, yi)), 1, None)



