import numpy as np
from src.agent import Agent

class Random_Frontier(Agent):
        
    def get_random_unnknown(self):
        unknown_points = np.argwhere(self.agent_map == self.cfg.UNKNOWN)
        if len(unknown_points) == 0:
            # return self.get_random_point()
            # print("#get_random_unnknown(): No unknown points")
            # set goal as current position
            self.plan = []
            self.area_completed = True
            return self.grid_position_xy
        elif len(unknown_points) == 1:
            return (unknown_points[0][1], unknown_points[0][0])
        # choose a random UNKNOWN
        idx = np.random.randint(len(unknown_points))
        return (unknown_points[idx][1], unknown_points[idx][0])

    def get_random_frontier(self):
        frontier_points = np.argwhere(self.agent_map == self.cfg.FRONTIER)
        if len(frontier_points) == 0:
            return self.get_random_unnknown()
        elif len(frontier_points) == 1:
            return (frontier_points[0][1], frontier_points[0][0])
        # choose a random frontier
        idx = np.random.randint(len(frontier_points))
        return (frontier_points[idx][1], frontier_points[idx][0])
    
    def get_goal_method(self):
        return self.get_random_frontier()
