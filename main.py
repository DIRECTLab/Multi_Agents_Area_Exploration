import random
import numpy as np
import pandas as pd
from multiprocessing import Pool, Manager, Process, Queue

from src.config import Config
from src.experiment import run_experiment, setup_experiment
from src.agent import Agent
from src.replan.frontier import *
from src.replan.voronoi_basic import *
from src.starting_scenario.starting_methods import *
from src.starting_scenario.goal_starts import *
from src.replan.decision import *
from src.darp.darp import *
from src.replan.epsilon_greedy import *

import itertools

def main():
    all_df = pd.DataFrame()
    df_index = 0
    
    process_manager = Manager()
    return_dict = process_manager.dict()
    Process_list = []
    ratio_list = [(50,50),(25,75)]
    
    Method_list = [
        # Frontier_Random,
        # Frontier_Closest,
        Voronoi_Frontier_Random,
        Voronoi_Frontier_Closest,
        Voronoi_Frontier_Help_Closest,
        Voronoi_Frontier_Help_Random,
        Decision_Frontier_Closest,
        # Darp,                                   # Requires the DRAW_SIM in config file to be True.
        # Decay_Epsilon_Greedy_Unknown,
        Decay_Epsilon_Greedy_Frontier,
        # Epsilon_Greedy_Unknown,
        # Epsilon_Greedy_Frontier,
        ]
    Start_scenario_list = [
        # Manual_Start,
        # Edge_Start_Position,
        # Top_Left_Start_Position,
        Rand_Start_Position,
        # Center_Start_Position,
        ]
    Start_Goal_list= [
        # Manual_Goal,
        Rand_Start_Goal,
        # Center_Start_Goal,
        # Top_Left_Start_Goal,
        # Edge_Start_Goal,
        # Distributed_Goal,
        ]

    All_scenarios = [ Start_scenario_list , Start_Goal_list]
    


    prosses_count = 0
    for map_length in range(50,100,50):
        for agent_count in range(4,10,2):
            print(f"map_length: {map_length} agent_count: {agent_count}")
            for start in Start_scenario_list:
                for goal in Start_Goal_list:
                    for Method in Method_list:
                        # if Method == "Heterogenus":
                        #     cur_Method_list = Method_list[:-1]
                        #     print("\n\n")
                        #     # get every combo of all the methods starting from 2 to the number of methods
                            
                        #     for combo in itertools.combinations(cur_Method_list, 2):
                        #         print(f"combo {len(combo)} {combo}")
                        #         method1 = combo[0]
                        #         method2 = combo[1]

                        #         # ratio assinment of the agents
                        #         for ratio in ratio_list:
                        #             method1_couint =  ratio[0]
                        #             method2_couint =  ratio[1]

                        # continue
                        cfg = Config()
                        cfg.SEED = int(map_length )
                        cfg.N_BOTS = int(agent_count)

                        random.seed(cfg.SEED)
                        np.random.seed(cfg.SEED)

                        cfg.COLS = int(map_length)
                        cfg.ROWS = int(map_length)
                        cfg.SCREEN_WIDTH = int(map_length*cfg.GRID_THICKNESS)
                        cfg.SCREEN_HEIGHT = int(map_length*cfg.GRID_THICKNESS)

                        experiment_name = f"test_{agent_count}_nbots:{cfg.N_BOTS}_rows:{cfg.ROWS}_cols:{cfg.COLS}_seed:{cfg.SEED}"
                        print(f"Starting Experiment: {experiment_name}")

                        Agent_Class = type('Agent_Class', (Method, start, goal), {})
                        

                        search_method =''.join(str(base.__name__)+'\n'  for base in Agent_Class.__bases__)
                        search_method += Agent_Class.__name__
                        print("Method:", search_method)

                        set_up_data = setup_experiment(cfg, experiment_name, Agent_Class, search_method, )

                        run_experiment(prosses_count, 
                                    return_dict,
                                    cfg,
                                    experiment_name, 
                                    search_method =search_method,
                                    set_up_data = set_up_data, 
                                    debug=True)
                        df_index += 1
    
    #             # run the simulation in a new process
    #             p = Process(target=run_experiment, 
    #                         args=(
    #                                 prosses_count, 
    #                                 return_dict,
    #                                 cfg,
    #                                 experiment_name, 
    #                                 search_method ,
    #                                 set_up_data , 
    #                             ))
    #             p.start()
    #             Process_list.append(p)
    #             prosses_count += 1

    # for p in Process_list:
    #     p.join()
    #     print("Joined Process: ", p.pid)
    
    # collect all the data
    for [df, cfg, full_map] in return_dict.values():
        all_df = all_df.append(df, ignore_index=True)

    all_df.to_csv(f"data/all_data.csv")

if __name__ == "__main__":
    main()
    # save the Conda environment yaml file so that we can recreate the environment on any machine
    import os
    # with out the prefix, the environment will be saved to the current directory
    os.system("conda env export --no-builds > environment.yml")
