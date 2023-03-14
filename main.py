import random
import numpy as np
import pandas as pd
from multiprocessing import Pool, Manager, Process, Queue

from src.config import Config
from src.experiment import run_experiment, setup_experiment
from src.agent import createBot
from src.replan.random_frontier import Random_Frontier
from src.replan.random_frontier_closest import Random_Frontier_Closest
from src.replan.voronoi_random_frontier import Voronoi_Random_Frontier
from src.replan.voronoi_random_closest_frontier import Voronoi_Random_Closest_Frontier

def main():
    all_df = pd.DataFrame()
    df_index = 0
    
    process_manager = Manager()
    return_dict = process_manager.dict()
    Process_list = [] 
    # create a pfrogress bar for each process thead
    Method_list = [
        Random_Frontier,
        Random_Frontier_Closest,
        Voronoi_Random_Frontier,
        Voronoi_Random_Closest_Frontier,
        ]


    prosses_count = 0
    for map_length in range(20,30,10):
        for agent_count in range(5,10,5):
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

                global Agent_Class 
                Agent_Class = createBot(method)
                search_method = f"{Agent_Class.__bases__[0].__name__}"
                print("Method:", Agent_Class.__bases__[0].__name__)

                set_up_data = setup_experiment(cfg, experiment_name, Agent_Class, search_method, )

                run_experiment(prosses_count, 
                            return_dict,
                            cfg,
                            experiment_name, 
                            search_method =search_method,
                            set_up_data = set_up_data, 
                            debug=True)
                df_index += 1
    
                # run the simulation in a new process
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