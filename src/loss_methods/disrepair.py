import numpy as np
from src.agent import Agent
import warnings


class Disrepair(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choose_random = False
        self.last_mutual_data_copy = None

    def check_should_replan(self, mutual_data):
        if len(mutual_data['Agent_Data'][self.id]['help']) > 0 and self.plan[-1] != mutual_data['Agent_Data'][self.id]['help'][0][1]:
                return True
        return super().check_should_replan(mutual_data)
    
    def update(self, mutual_data, draw=True):

        if self.still_disabled(mutual_data):
            return
        return super().update(mutual_data, draw)
    

    def move(self, mutual_data):
        if self.check_for_hit_mine(mutual_data):
                return
        return super().move(mutual_data)
    

    def check_for_hit_mine(self, mutual_data):
        cur_x = self.grid_position_xy[0]
        cur_y = self.grid_position_xy[1]
        next_path_point = self.plan[0]
        if self.ground_truth_map[next_path_point[0], next_path_point[1]] == self.cfg.MINE:
            # If we are unrecoverable, then no one can help us
            if self.cfg.ROBOT_LOSS_TYPE == 'Unrecoverable':
                self.disabled = True
                return

            # Another non-disabled teammate can come help us
            agent_locations_and_id = []
            agent_locations = []
            for agent_id in mutual_data['Agent_Data']:
                if self.id == agent_id or mutual_data['Agent_Data'][agent_id]['disabled']:
                    continue
                agent_locations_and_id.append((agent_id, mutual_data['Agent_Data'][agent_id]['grid_position_xy']))
                agent_locations.append(mutual_data['Agent_Data'][agent_id]['grid_position_xy'])

            if len(agent_locations) == 0:
                warnings.warn("No viable agents available to help")
                return
            # Find the closest teammate
            closest = self.get_closest_point_rc(agent_locations)
            closest = (closest[0], closest[1])
            for agent_info in agent_locations_and_id:
                if agent_info[1] == closest:
                    # If a teammate is right next to us, then they can just help us
                    if abs(closest[0] - cur_x) <= 1 and abs(closest[1] - cur_y) <= 1:
                        break
                    cur_pos = (self.grid_position_xy[0], self.grid_position_xy[1])
                    mutual_data['Agent_Data'][agent_info[0]]['help'].append((self.id, cur_pos))
                    self.disabled = True
                    mutual_data['Agent_Data'][self.id]['disabled'] = True
                    self.ground_truth_map[next_path_point[0], next_path_point[1]] = self.cfg.EMPTY
                    return True
        return False