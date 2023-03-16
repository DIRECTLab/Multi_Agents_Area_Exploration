import numpy as np

class Rand_Start:
    def choose_start(self):
        self.grid_position_xy = self.get_random_point()
        self.goal_xy = self.get_random_point()


class Center_Start:
    def choose_start(self):
        center_xy = (int(self.cfg.COLS//2), int(self.cfg.ROWS//2))
        self.grid_position_xy = center_xy
        self.goal_xy = self.get_random_point()


class Top_Left_Start:
    def choose_start(self):
        self.grid_position_xy = (1, 1)
        self.goal_xy = self.get_random_point()

class Edge_Start:
    def choose_start(self):
        self.grid_position_xy = points_on_rectangle_edge(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS)[self.id]
        self.grid_position_xy = (int(np.round(self.grid_position_xy[0])), \
                                int(np.round(self.grid_position_xy[1])))
        # check if the point is not on an obstacle
        if self.ground_truth_map[self.grid_position_xy[1], self.grid_position_xy[0]] == self.cfg.OBSTACLE:
            # if point is the top or bottom edge move it to the left or right randomly
            # +1 or -1 to avoid the obstacle
            sub_or_add_One = np.random.choice([-1,1])
            if self.grid_position_xy[1] == 0 or self.grid_position_xy[1] == self.cfg.ROWS-1:
                self.grid_position_xy = (self.grid_position_xy[0]+sub_or_add_One, self.grid_position_xy[1])
            # if point is the left or right edge move it up or down randomly
            elif self.grid_position_xy[0] == 0 or self.grid_position_xy[0] == self.cfg.COLS-1:
                self.grid_position_xy = (self.grid_position_xy[0], self.grid_position_xy[1]+sub_or_add_One)


        self.goal_xy = self.get_random_point()



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
