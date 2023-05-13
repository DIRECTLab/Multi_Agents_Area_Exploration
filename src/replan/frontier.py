import numpy as np
from src.agent import Agent

class Frontier_Closest(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choose_random = False
        
    def get_goal_method(self):
        # Get a random frontier point
        frontier_point = self.get_new_location_xy(self.agent_map, self.cfg.FRONTIER, useRandom=self.choose_random)
        if frontier_point:
            return frontier_point
        
        # Get a random unknown point
        unknown_point = self.get_new_location_xy(self.agent_map, self.cfg.UNKNOWN,  useRandom=self.choose_random)
        if unknown_point is None:
            self.plan = []
            self.area_completed = True
            return self.grid_position_xy
        
        if unknown_point[0] == 0:
            unknown_point = (1, unknown_point[1])
        if unknown_point[0] == len(self.agent_map) - 1:
            unknown_point = (unknown_point[0] - 1, unknown_point[1])
        if unknown_point[1] == 0:
            unknown_point = (unknown_point[0], 1)
        if unknown_point[1] == len(self.agent_map[0]) - 1:
            unknown_point = (unknown_point[0], unknown_point[1] - 1)
        
        return unknown_point


class Frontier_Random(Frontier_Closest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choose_random = True


class Unknown_Closest(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choose_random = False

    def get_goal_method(self):
        unknown_point = self.get_new_location_xy(self.agent_map, self.cfg.UNKNOWN,  useRandom=self.choose_random)
        if unknown_point is None:
            self.plan = []
            self.area_completed = True
            return self.grid_position_xy
        return unknown_point
    
class Unknown_Random(Unknown_Closest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choose_random = True

