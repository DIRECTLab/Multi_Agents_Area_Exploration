import numpy as np
from src.agent import Agent

class Actions:
  def __init__(self, m):
    self.m = m
    self.mean = 0
    self.N = 0
  
  # Choose a random action
  def choose(self): 
    return np.random.randn() + self.m
  
  # Update the action-value estimate
  def update(self, x):
    self.N += 1
    self.mean = (1 - 1.0 / self.N)*self.mean + 1.0 / self.N * x

class Epsilon_Greedy(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.epsilon = 0.1
        self.random_frontier = False
        self.m1 = 1
        self.m2 = 2
        self.m3 = 3

    def get_goal_method(self):

        actions = [Actions(self.m1), Actions(self.m2), Actions(self.m3)]
        
        # TODO: Figure out how to incorporate this data array. 
        # I could make it a class variable, but I don't know how big N should 
        # be since the agent will run for an unknown amount of time.
        data = np.empty(N)
            
        for i in range(self.N):
            # epsilon greedy
            p = np.random.random()
            if p < self.epsilon:
                j = np.random.choice(3)
            else:
                j = np.argmax([a.mean for a in actions])
                x = actions[j].choose()
                actions[j].update(x)
        
            # for the plot
            data[i] = x
        cumulative_average = np.cumsum(data) / (np.arange(N) + 1)
        
        return cumulative_average