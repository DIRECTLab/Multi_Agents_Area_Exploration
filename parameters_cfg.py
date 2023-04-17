import numpy as np
from src.config import Config

from src.agent import Agent
from src.replan.frontier import *
from src.replan.voronoi_basic import *
from src.starting_scenario.starting_methods import *
from src.starting_scenario.goal_starts import *
from src.replan.decision import *
from src.darp.darp import *
from src.replan.epsilon_greedy import *
from src.replan.game_theory import *

class Parameters:
    def __init__(self):
        repeat_count =1

        self.Debug = False
        self.Use_process = False
        self.Create_gif = False
        assert not (self.Debug and self.Use_process), "Can't use process and debug at the same time"

        # The length of the map    
        self.map_length_list = list(range(50,100,20))

        # The number of agents in the experiment
        self.agent_count_list = list(range(4,10,2))

        # iteration_repeat_experiment will be used to repeat the experiment
        self.iteration_repeat_experiment = list(range(0, 60))

        self.Method_list = [
            Frontier_Random,
            Frontier_Closest,
            Unknown_Random,
            Unknown_Closest,
            Voronoi_Frontier_Random,
            Voronoi_Frontier_Closest,
            Voronoi_Frontier_Help_Closest,
            Voronoi_Frontier_Help_Random,
            Decision_Frontier_Closest,
            # DarpVorOnly,
            # DarpMST,
            Decay_Epsilon_Greedy_Unknown,
            Decay_Epsilon_Greedy_Frontier,
            Epsilon_Greedy_Unknown,
            Epsilon_Greedy_Frontier,
            GameTheory,
            # "Heterogenus",
            ]
        self.Start_scenario_list = [
            # # Manual_Start,
            Rand_Start_Position,
            # Edge_Start_Position, # does not work with Voronoi methods Currently
            # Top_Left_Start_Position,
            # Center_Start_Position, 
            ]
        self.Start_Goal_list= [
            # # Manual_Goal,
            Rand_Start_Goal,
            # Center_Start_Goal, # does not work with Voronoi methods Currently
            # Top_Left_Start_Goal, # does not work with Voronoi methods Currently
            # Edge_Start_Goal, 
            # Distributed_Goal,
            ]
        
        self.Robot_Loss = [
            # "Safe_Run"
            "Disrepair",
            "Unrecoverable",
        ]



        # use a dic instead of a list to make it easier to read
        self.All_scenarios_dic = {
            "Method": self.Method_list,
            "Loss": self.Robot_Loss,
            "Start": self.Start_scenario_list,
            "Goal": self.Start_Goal_list,
            "Map Length": self.map_length_list,
            "Agent Count": self.agent_count_list,
            "Experiment Iteration": self.iteration_repeat_experiment
        }
