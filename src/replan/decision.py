# from src.replan.frontier import Frontier_Closest
from src.replan.frontier import *
# src/replan/frontier.py
import numpy as np

class Decision_Frontier_Closest(Unknown_Random):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    # def save_to_mutual_data(self, mutual_data):
    #     mutual_data['Agent_Data'][self.id]['plan'] = self.plan
    #     mutual_data['Agent_Data'][self.id]['goal_xy'] = self.goal_xy
    #     mutual_data['Agent_Data'][self.id]['grid_position_xy'] = self.grid_position_xy
    
    def update(self, mutual_data, draw=True):
        if 'Agent_Data' not in mutual_data:
            mutual_data['Agent_Data'] = {} 
        if self.id not in mutual_data['Agent_Data']:
            mutual_data['Agent_Data'][self.id] = {}
            self.save_to_mutual_data(mutual_data)


        for OTHER_AGENT_ID in mutual_data['Agent_Data']:
            if OTHER_AGENT_ID == self.id:
                continue
            other_agent_data = mutual_data['Agent_Data'][OTHER_AGENT_ID]
            if other_agent_data['goal_xy'] is None or self.goal_xy is None:
                # The other agent needs to replan
                continue
            dist = np.sqrt((self.goal_xy[0] - other_agent_data['goal_xy'][0])**2 \
                        + (self.goal_xy[1] - other_agent_data['goal_xy'][1])**2)
            if dist < self.lidarRange:
                # print(f"Agents self:{self.id} and Other: {OTHER_AGENT_ID} are close to each other")
                # print(f"At the goals: self:{self.goal_xy} and other: {other_agent_data['goal_xy']}")

                
                # compare plans coasts
                # and if we are closer to the goal, then we should win the goal

                if len(other_agent_data['plan']) > len(self.plan):
                    #  at this point the OTHER-agent has a longer plan
                    # They loose the goal 
                    mutual_data['Agent_Data'][OTHER_AGENT_ID]['plan'] = []

                    # we have a shorter plan, we can take the goal0
                    # we need to pick a new goal for self
                    self.save_to_mutual_data(mutual_data)
                    self.choose_random = False
                    return super().update(mutual_data, draw)
                else:
                    # we have a longer plan, we loose the goal
                    self.plan= []
                    self.goal_xy = None
                    self.choose_random = True
                    # mutual_data['Agent_Data'][self.id]['plan'] = []
                    # mutual_data['Agent_Data'][self.id]['goal_xy'] = None
                    # mutual_data['Agent_Data'][self.id]['grid_position_xy'] = self.grid_position_xy

        super_return = super().update(mutual_data, draw)
        self.save_to_mutual_data(mutual_data)
        return super_return
    