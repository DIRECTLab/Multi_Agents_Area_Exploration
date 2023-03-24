import numpy as np
from src.agent import Agent

class Frontier_Closest(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.random_frontier = False
        
    def get_goal_method(self):
        # Get a random frontier point
        frontier_point = self.get_new_location_xy(self.agent_map, self.cfg.FRONTIER, useRandom=self.random_frontier)
        if frontier_point:
            return frontier_point
        
        # Get a random unknown point
        unknown_point = self.get_new_location_xy(self.agent_map, self.cfg.UNKNOWN,  useRandom=self.random_frontier)
        if unknown_point is None:
            self.plan = []
            self.area_completed = True
            return self.grid_position_xy
        
        return unknown_point


class Frontier_Random(Frontier_Closest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.random_frontier = True


class Unknown_Closest(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.random_unknown = False

    def get_goal_method(self):
        unknown_point = self.get_new_location_xy(self.agent_map, self.cfg.UNKNOWN,  useRandom=self.random_unknown)
        if unknown_point is None:
            self.plan = []
            self.area_completed = True
            return self.grid_position_xy
        return unknown_point
    
class Unknown_Random(Unknown_Closest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.random_unknown = True