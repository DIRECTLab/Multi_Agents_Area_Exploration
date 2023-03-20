import numpy as np
from src.agent import Agent

class Random_Frontier(Agent):
            
    def get_goal_method(self):
        # Get a random frontier point
        frontier_point = self.get_random_new_location_xy(self.agent_map, self.cfg.FRONTIER)
        if frontier_point:
            return frontier_point
        
        # Get a random unknown point
        unknown_point = self.get_random_new_location_xy(self.agent_map, self.cfg.UNKNOWN)
        if unknown_point is None:
            self.plan = []
            self.area_completed = True
            return self.grid_position_xy
        
        return unknown_point
