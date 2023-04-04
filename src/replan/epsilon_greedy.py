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
          self.choose_random_unknown = not self.choose_random_unknown

        return super().get_goal_method()

class Epsilon_Greedy_Frontier(Frontier_Random):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.epsilon = 0.1

    def get_goal_method(self):
        p = np.random.random()
        if p > self.epsilon:
          self.choose_random_frontier = not self.choose_random_frontier

        return super().get_goal_method()

class Decay_Epsilon_Greedy_Unknown(Epsilon_Greedy_Unknown):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.epsilon = 1.0

      def get_goal_method(self):
        decay_rate = 1.0 / (self.frame_count * self.ground_truth_map.shape[0] * self.ground_truth_map.shape[1])

        self.epsilon -= decay_rate
        return super().get_goal_method()


class Decay_Epsilon_Greedy_Frontier(Epsilon_Greedy_Frontier):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.epsilon = 1.0


      def get_goal_method(self):
        decay_rate = 1.0 / (self.frame_count * self.ground_truth_map.shape[0] * self.ground_truth_map.shape[1])

        self.epsilon -= decay_rate
        return super().get_goal_method()