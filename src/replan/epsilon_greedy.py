import numpy as np
from src.agent import Agent
from src.replan.frontier import *


class Epsilon_Greedy_Unknown(Unknown_Random):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.epsilon = 0.1

    def get_goal_method(self):
        p = np.random.random()
        if p > self.epsilon:
          self.choose_random = False
        else:
          self.choose_random = True

        return super().get_goal_method()

class Epsilon_Greedy_Frontier(Frontier_Random):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.epsilon = 0.1

    def get_goal_method(self):
        p = np.random.random()
        if p > self.epsilon:
          self.choose_random = False
        else:
          self.choose_random = True

        return super().get_goal_method()

class Decay_Epsilon_Greedy_Unknown(Epsilon_Greedy_Unknown):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.epsilon = 1.0

      def get_goal_method(self):
        decay_rate = 1.0 / self.frame_count + 0.00001
        self.epsilon = decay_rate
        return super().get_goal_method()


class Decay_Epsilon_Greedy_Frontier(Epsilon_Greedy_Frontier):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.epsilon = 1.0

      def get_goal_method(self):
        self.epsilon = np.where(self.agent_map == self.cfg.UNKNOWN, 1, 0).sum() / self.agent_map.size     
        return super().get_goal_method()
      
