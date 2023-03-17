import random
import numpy as np
import pandas as pd
from multiprocessing import Pool, Manager, Process, Queue
import itertools

from src.config import Config
from src.experiment import run_experiment, setup_experiment
from src.agent import createBot
from src.replan.random_frontier import Random_Frontier
from src.replan.random_frontier_closest import Random_Frontier_Closest
from src.replan.voronoi_random_frontier import Voronoi_Random_Frontier
from src.replan.voronoi_random_closest_frontier import Voronoi_Random_Closest_Frontier
from src.starting_scenario.starting_methods import *
from src.starting_scenario.goal_starts import *

def main():
    all_df = pd.DataFrame()
    df_index = 0
    
    process_manager = Manager()
    return_dict = process_manager.dict()
    Process_list = [] 
    
    Method_list = [
        # Random_Frontier,
        # Random_Frontier_Closest,
        Voronoi_Random_Frontier,
        # Voronoi_Random_Closest_Frontier,
        ]
    Start_scenario_list = [
        # Edge_Start_Position,
        Top_Left_Start_Position,
        # Rand_Start_Position,
        # Center_Start_Position,
        ]
    Start_Goal_list= [
        # Rand_Start_Goal,
        # Center_Start_Goal,
        # Top_Left_Start_Goal,
        # Edge_Start_Goal,
        Distributed_Goal,
        ]

    All_scenarios = [Method_list , Start_scenario_list , Start_Goal_list]
    


    prosses_count = 0
    for map_length in range(20,30,10):
        for agent_count in range(4,10,2):
            for scenario_base_classes in itertools.product(*All_scenarios):

                cfg = Config()
                cfg.SEED = int(map_length )
                cfg.N_BOTS = int(agent_count)

                random.seed(cfg.SEED)
                np.random.seed(cfg.SEED)

                cfg.COLS = int(map_length)
                cfg.ROWS = int(map_length)
                cfg.SCREEN_WIDTH = int(map_length*cfg.GRID_THICKNESS)
                cfg.SCREEN_HEIGHT = int(map_length*cfg.GRID_THICKNESS)

                # TODO Populate START_CENTROID_LIST_XY 

                experiment_name = f"test_{agent_count}_nbots:{cfg.N_BOTS}_rows:{cfg.ROWS}_cols:{cfg.COLS}_seed:{cfg.SEED}"
                print(f"Starting Experiment: {experiment_name}")
   
                Agent_Class = createBot(scenario_base_classes)
                search_method =''.join(str(base.__name__)+'\n'  for base in Agent_Class.__bases__)
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
