import numpy as np
from src.config import *

class rand_frontier:
    def __init__(self, agent_map, agent_pos, full_map):
        self.agent_map = agent_map
        self.agent_pos = agent_pos
        self.full_map = full_map
    def get_random_point(self):
        # make sure the goal is not in the obstacle
        while True:
            goal = (np.random.randint(self.full_map.shape[0]), np.random.randint(self.full_map.shape[1]))
            if self.full_map[goal] == True:
                break
        return goal
        
    def get_random_unnknown(self):
        unknown_points = np.argwhere(self.agent_map == UNKNOWN)
        if len(unknown_points) == 0:
            return self.get_random_point()
        elif len(unknown_points) == 1:
            return (unknown_points[0][1], unknown_points[0][0])
        # choose a random UNKNOWN
        idx = np.random.randint(len(unknown_points))
        return (unknown_points[idx][1], unknown_points[idx][0])

    def get_random_frontier(self):
        frontier_points = np.argwhere(self.agent_map == FRONTIER)
        if len(frontier_points) == 0:
            return self.get_random_unnknown()
        elif len(frontier_points) == 1:
            return (frontier_points[0][1], frontier_points[0][0])
        # choose a random frontier
        idx = np.random.randint(len(frontier_points))
        return (frontier_points[idx][1], frontier_points[idx][0])

        