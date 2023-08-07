import numpy as np
from src.agent import Agent
import warnings


class Unrecoverable(Agent):
    def __init__(self, *args, **kwargs):
        # check if any mines are in the  self.ground_truth_map
        super().__init__(*args, **kwargs)
        if not np.any(self.ground_truth_map == self.cfg.MINE):
            # abourt if there are no mines            
            print("🛑 Experiment Failed:: there are no mines")
            exit(1)

    def check_should_replan(self, mutual_data):
        if len(mutual_data['Agent_Data'][self.id]['help_request_list']) > 0 and self.plan[-1] != mutual_data['Agent_Data'][self.id]['help_request_list'][0]['other_agent_pos']:
                return True
        return super().check_should_replan(mutual_data)

    def check_for_hit_mine(self, mutual_data):
        cur_x = self.grid_position_xy[0]
        cur_y = self.grid_position_xy[1]
        next_path_point = self.plan[0]
        if self.ground_truth_map[next_path_point[0], next_path_point[1]] == self.cfg.MINE:
            # If we are unrecoverable, then no one can help us
            self.disabled = True
            return True
        return False
        
    def move(self, mutual_data):
        if self.check_for_hit_mine(mutual_data):
            return
        return super().move(mutual_data)
    
    def still_disabled(self, mutual_data):        
        return self.disabled

    def update(self, mutual_data, draw=True):

        if self.still_disabled(mutual_data):
            return
        return super().update(mutual_data, draw)