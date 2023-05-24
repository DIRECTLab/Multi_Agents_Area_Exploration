import numpy as np
from src.agent import Agent
from src.point_utils.point_find import *

class Frontier_Closest(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choose_random = False
        
    def get_goal_method(self):
        # Get a random frontier point
        frontier_point = get_new_location_xy(self.agent_map, self.cfg.FRONTIER, useRandom=self.choose_random, closest_point_to_xy= self.grid_position_xy)
        if frontier_point:
            return frontier_point
        
        # Get a random unknown point
        unknown_point = get_new_location_xy(self.agent_map, self.cfg.UNKNOWN,  useRandom=self.choose_random, closest_point_to_xy= self.grid_position_xy)
        if unknown_point is None:
            self.plan = []
            self.area_completed = True
            return self.grid_position_xy
        
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
        unknown_point = get_new_location_xy(self.agent_map, self.cfg.UNKNOWN,  useRandom=self.choose_random, closest_point_to_xy= self.grid_position_xy)
        if unknown_point is None:
            self.plan = []
            self.area_completed = True
            return self.grid_position_xy
        return unknown_point
    
class Unknown_Random(Unknown_Closest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choose_random = True

