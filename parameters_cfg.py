import numpy as np
from src.config import Config

# Robot Loss
from src.agent import Agent
from src.loss_methods.unrecoverable import Unrecoverable
from src.loss_methods.disrepair import Disrepair

# Replan methods
from src.replan.frontier import *
from src.replan.voronoi_basic import *
from src.starting_scenario.starting_methods import *
from src.replan.decision import *
from src.darp.darp import *
from src.replan.epsilon_greedy import *
from src.replan.game_theory import *


class Parameters:
    def __init__(self):

        self.Debug = True
        self.Use_process = False
        self.Create_gif = False
        assert not (self.Debug and self.Use_process), "Can't use process and debug at the same time"

        # The length of the map
        self.map_length_list = [150] #list(range(30,91,30))

        # The number of agents in the experiment
        # self.agent_count_list = list(range(2,10,2))
        # self.agent_count_list = [4,8,12]
        self.agent_count_list = [4]
        # self.agent_count_list = [12]
        assert np.array(self.agent_count_list).max() <13, "The number of agents should be less than 13"
        
        # iteration_repeat_experiment will be used to repeat the experiment
        # self.iteration_repeat_experiment = list(range(0, 30))
        self.iteration_repeat_experiment = [1]

        # self.min_rom_size = [4,12,20]
        self.min_rom_size = [20]
        # self.min_rom_size = [3,6,9,12,30]

        self.Method_list = [
            # Frontier_Random,
            Frontier_Closest,
            # Unknown_Random,
            # Unknown_Closest,

            # # @@@@@@@@ Voronoi_Frontier_Random,
            # # @@@@@@@@ Voronoi_Frontier_Closest,
            # Voronoi_Frontier_Help_Closest,
            # Voronoi_Frontier_Help_Random,
            
            # Decision_Frontier_Closest,
            # Decay_Epsilon_Greedy_Unknown,
            # Decay_Epsilon_Greedy_Frontier,
            # # Epsilon_Greedy_Unknown,
            # # Epsilon_Greedy_Frontier,
            # GameTheory,

            # DarpVorOnly,
            # DarpMST,

            # # # "Heterogenus",
            ]
        # make sure the list is dose not contain duplicates
        self.Method_list = list(set(self.Method_list))

        self.Start_scenario_list = [
            # # Manual_Start,
            Rand_Start,
            # Edge_Start,
            # Top_Left_Start,
            # Center_Start,
            # Distributed_Start,
            ]
        self.Start_Goal_list= [
            # # Manual_Start,
            Rand_Start,
            # Edge_Start,
            # Top_Left_Start,
            # Center_Start,
            # Distributed_Start,
            ]
        
        self.Robot_Loss = [
            Agent,
            # Unrecoverable,
            # Disrepair,
        ]



        # use a dic instead of a list to make it easier to read
        self.All_scenarios_dic = {
            "Method": self.Method_list,
            "Loss": self.Robot_Loss,
            "Start": self.Start_scenario_list,
            "Goal": self.Start_Goal_list,
            "Map Length": self.map_length_list,
            "Agent Count": self.agent_count_list,
            "Experiment Iteration": self.iteration_repeat_experiment,
            "Min Room Size": self.min_rom_size,
        }
