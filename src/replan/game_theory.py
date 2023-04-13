import numpy as np
from src.agent import Agent
from src.replan.frontier import *

class GameTheory(Frontier_Closest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choose_random = False
        self.last_mutual_data_copy = None

    def save_to_mutual_data(self, mutual_data):
        super().save_to_mutual_data(mutual_data)

        # TODO find a more efficient way to do this!!!
        self.last_mutual_data_copy = mutual_data.copy()


    def get_goal_method(self):
        # Get a random frontier point
        # read the mutual data and choose the anti majority choose_random
        true_count, false_count = 0, 0

        least_majority = None
        bool_list = []
        
        for i in self.last_mutual_data_copy['Agent_Data']:
            bool_list.append(self.last_mutual_data_copy['Agent_Data'][i]['choose_random'])

        true_count = bool_list.count(True)
        false_count = bool_list.count(False)

        if true_count == false_count:
            least_majority = np.random.choice([True, False])
        else:
            if true_count < false_count:
                least_majority = True
            else:
                least_majority = False

        self.choose_random = least_majority
        self.last_mutual_data_copy['Agent_Data'][self.id]['choose_random'] = least_majority

        return super().get_goal_method()
