import numpy as np

class Rand_Start_Position:
    def choose_start_position(self):
        self.grid_position_xy = self.get_random_point()

class Center_Start_Position:
    def choose_start_position(self):
        center_xy = (int(self.cfg.COLS//2), int(self.cfg.ROWS//2))
        self.grid_position_xy = center_xy

class Top_Left_Start_Position:
    def choose_start_position(self):
        top_left_xy = (1, 1)
        self.grid_position_xy = top_left_xy

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
            if foundPoint:
                return
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.grid_position_xy)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.grid_position_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.grid_position_xy)
            return
            
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
            x = 0 +shift
            y = center[1] - radius * np.sin(angle)
        elif x > cols:
            x = cols -shift
            y = center[1] + radius * np.sin(angle)
        elif y < 0:
            y = 0+shift
            x = center[0] - radius * np.cos(angle)
        elif y > rows:
            y = rows-shift
            x = center[0] + radius * np.cos(angle)
        points[i, 0] = x
        points[i, 1] = y
    return points

def check_if_valid_point(point, ground_truth_map, cfg):
    point = point
    # choose a fandome point from the 8 neighbors
    neighbors = [(point[0]+1, point[1]), \
                (point[0]-1, point[1]), \
                (point[0], point[1]+1), \
                (point[0], point[1]-1), \
                (point[0]+1, point[1]+1), \
                (point[0]-1, point[1]+1), \
                (point[0]+1, point[1]-1), \
                (point[0]-1, point[1]-1)]
    
    # shuffle the neighbors
    np.random.shuffle(neighbors)
    for cur_point in neighbors:
        # check if the point is in the map
        if cur_point[0] < 0 or cur_point[0] >= cfg.COLS or \
            cur_point[1] < 0 or cur_point[1] >= cfg.ROWS:
            continue
        if ground_truth_map[cur_point[1], cur_point[0]] == cfg.EMPTY:
            point = cur_point
            return True
    return False