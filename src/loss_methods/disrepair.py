import numpy as np
from src.agent import Agent
from src.loss_methods.unrecoverable import Unrecoverable
import warnings
from src.planners.astar_new import astar



class Disrepair(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def check_for_hit_mine(self, mutual_data):
        cur_x = self.grid_position_xy[0]
        cur_y = self.grid_position_xy[1]
        next_path_point = self.plan[0]
        if self.ground_truth_map[next_path_point[0], next_path_point[1]] == self.cfg.MINE:
            self.ground_truth_map[next_path_point[0], next_path_point[1]] = self.cfg.EMPTY
            mutual_data['map'][next_path_point[0], next_path_point[1]] = self.cfg.EMPTY

            # Another non-disabled teammate can come help us
            agent_locations_and_id = []
            agent_locations = []
            for agent_id in mutual_data['Agent_Data']:
                if self.id == agent_id or mutual_data['Agent_Data'][agent_id]['disabled']:
                    continue
                agent_locations_and_id.append((agent_id, mutual_data['Agent_Data'][agent_id]['grid_position_xy']))
                pos = mutual_data['Agent_Data'][agent_id]['grid_position_xy']
                agent_locations.append((pos[1], pos[0]))

            if len(agent_locations) == 0:
                warnings.warn("No viable agents available to help")
                return
            # Find the closest teammate
            closest = self.get_closest_point_rc(agent_locations)
            closest = (closest[1], closest[0])
            for agent_info in agent_locations_and_id:
                if agent_info[1] == closest:
                    # If a teammate is right next to us, then they can just help us
                    if abs(closest[0] - cur_x) <= 1 and abs(closest[1] - cur_y) <= 1:
                        break
                    cur_pos = (self.grid_position_xy[0], self.grid_position_xy[1])
                    # Inform the teammate that they need to help us

                    mutual_data['Agent_Data'][agent_info[0]]['help_request_list'].append({'other_agent_ID':self.id, 'other_agent_pos':cur_pos})
                    self.disabled = True
                    mutual_data['Agent_Data'][self.id]['disabled'] = True
                    # Remove the mine from the ground truth map
                    return True
        return False

    def still_disabled(self, mutual_data):
        if 'Agent_Data' in mutual_data and self.id in mutual_data['Agent_Data']:
            # See if we have been helped
            self.disabled = mutual_data['Agent_Data'][self.id]['disabled']
        return self.disabled
    
    def check_should_replan(self, mutual_data):
        if len(mutual_data['Agent_Data'][self.id]['help_request_list']) > 0 and not self.area_completed:
            if self.plan == None:
                return True
            if len(self.plan) == 0: # if we do this we get stuck in a loop
                return True
            if self.plan[-1] != mutual_data['Agent_Data'][self.id]['help_request_list'][0]['other_agent_pos']:
                # We found a new help request
                return True
        return super().check_should_replan(mutual_data)
    
    def replan_to_help(self, mutual_data):        
        if 'Agent_Data' in mutual_data and len(mutual_data['Agent_Data'][self.id]['help_request_list']) > 0:
            self.plan = astar( np.where(self.agent_map == self.cfg.KNOWN_WALL, self.cfg.KNOWN_WALL, self.cfg.KNOWN_EMPTY), 
                            (int(np.round(self.grid_position_xy[0])), int(np.round(self.grid_position_xy[1]))),
                            mutual_data['Agent_Data'][self.id]['help_request_list'][0]['other_agent_pos'])
            if self.plan == None:

                if self.replan_count > 100:
                    warnings.warn("Replan count is too high")
                assert self.replan_count < self.agent_map.size, "Replan count is too high 200"                
            return True
        return False

    def replan(self, mutual_data):
        if self.replan_to_help(mutual_data):
            return
        return super().replan(mutual_data)
    
    def help_teammate(self, mutual_data):
        if len(mutual_data['Agent_Data'][self.id]['help_request_list']) > 0:
            next_help_pos = mutual_data['Agent_Data'][self.id]['help_request_list'][0]['other_agent_pos']
            if abs(next_help_pos[0] - self.grid_position_xy[0]) <= 2 and abs(next_help_pos[1] - self.grid_position_xy[1]) <= 2:
                id = mutual_data['Agent_Data'][self.id]['help_request_list'][0]['other_agent_ID']
                mutual_data['Agent_Data'][id]['disabled'] = False
                mutual_data['Agent_Data'][self.id]['help_request_list'].pop(0)
    
    def move(self, mutual_data):
        self.help_teammate(mutual_data)
        if self.check_for_hit_mine(mutual_data):
            return

        return super().move(mutual_data)
    
    def update(self, mutual_data, draw=True):
        if self.plan == None:
            print(f"{self.id} Plan is none")

        if self.still_disabled(mutual_data):
            return
        return super().update(mutual_data, draw)