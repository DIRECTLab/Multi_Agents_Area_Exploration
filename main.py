import random
import numpy as np
import pandas as pd
from multiprocessing import Pool, Manager, Process, Queue

from src.config import Config
from src.experiment import run_experiment

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
    
    do_theading = True
    for k in range(50,51,1):
        for i in range(4,20,10):

            random.seed(int(i))
            np.random.seed(int(i))
            cfg = Config()
            cfg.SEED = int(i)
            cfg.N_BOTS = int(i)

            cfg.COLS = int(k)
            cfg.ROWS = int(k)
            cfg.SCREEN_WIDTH = int(k*cfg.GRID_THICKNESS)
            cfg.SCREEN_HEIGHT = int(k*cfg.GRID_THICKNESS)

            experiment_name = f"test_{i}_nbots{cfg.N_BOTS}_rows{cfg.ROWS}_cols{cfg.COLS}_seed{cfg.SEED}"
            print(f"Starting Experiment: {experiment_name}")

            # do_theading = not do_theading
            # cfg.USE_THREADS =do_theading
            print("cfg.USE_THREADS", cfg.USE_THREADS)

            run_experiment(df_index, return_dict, cfg, experiment_name, search_methods)
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