import random
import numpy as np
import pandas as pd
from multiprocessing import Pool, Manager, Process, Queue

from src.config import Config
from src.experiment import run_experiment
from src.replan.rand_horizen import *
from src.replan.voronoi_random import *
from src.agent import createBot

def main():
    all_df = pd.DataFrame()
    df_index = 0
    
    process_manager = Manager()
    return_dict = process_manager.dict()
    Process_list = []

    search_methods = { 
        'Use_Vernoi_method' : True,
        }
    
    # create a pfrogress bar for each process thead
    Method_list = [
        Rand_Frontier,
        #Rand_Closest_Frontier,
        Rand_Voronoi, 
        Closest_Voronoi,
        ]
    for map_length in range(20,100,10):
        for agent_count in range(2,10,2):
            for method_id, method in enumerate(Method_list):

                cfg = Config()
                cfg.SEED = int(map_length )
                cfg.N_BOTS = int(agent_count)

                random.seed(cfg.SEED)
                np.random.seed(cfg.SEED)

                cfg.COLS = int(map_length)
                cfg.ROWS = int(map_length)
                cfg.SCREEN_WIDTH = int(map_length*cfg.GRID_THICKNESS)
                cfg.SCREEN_HEIGHT = int(map_length*cfg.GRID_THICKNESS)

                experiment_name = f"test_{agent_count}_nbots{cfg.N_BOTS}_rows{cfg.ROWS}_cols{cfg.COLS}_seed{cfg.SEED}"
                print(f"Starting Experiment: {experiment_name}")

                # do_theading = not do_theading
                # cfg.USE_THREADS =do_theading
                print("cfg.USE_THREADS", cfg.USE_THREADS)

                Agent_Class = createBot(method)
                print("Method:", Agent_Class.__bases__[0].__name__)
                run_experiment(df_index, return_dict, cfg, experiment_name, search_methods, Agent_Class=Agent)
    #             df_index += 1
    #             # # run the simulation in a new process
    #             p = Process(target=run_experiment, args=(i, return_dict,cfg,experiment_name, search_methods))
    #             p.start()
    #             Process_list.append(p)

    # for p in Process_list:
    #     p.join()
    #     print("Joined Process: ", p.pid)
    
    # collect all the data
    for [df, cfg, full_map] in return_dict.values():
        all_df = all_df.append(df, ignore_index=True)

    all_df.to_csv(f"data/all_data.csv")

if __name__ == "__main__":
    main()