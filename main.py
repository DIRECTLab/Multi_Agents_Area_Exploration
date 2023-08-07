import random
import numpy as np
import pandas as pd
import os
# from multiprocessing import Pool, Manager, Process, Queue
import multiprocessing as mp

from src.experiment import *
from src.config import Config

import itertools
import tqdm

def run_scenario(args):
    scenario, parameters, return_dict, prosses_count, debug = args
    print_string =""
    for i, [key,value, cur_list] in enumerate(zip(parameters.All_scenarios_dic.keys(), scenario, parameters.All_scenarios_dic.values())):
        cur_list = list(cur_list)

        if type(value) == type:
            # GREEN color for classes
            print_string += f"| {key:<30} | \033[92m{value.__name__:<30}\033[00m | {cur_list.index(value)+1}/{len(cur_list)} \n"
        elif callable(value):
            # BLUE color for functions
            print_string += f"| {key:<30} | \033[94m{value.__name__:<30}\033[00m | {cur_list.index(value)+1}/{len(cur_list)} \n"
        elif isinstance(value, str):
            # RED color for strings
            print_string += f"| {key:<30} | \033[91m{value:<30}\033[00m | {cur_list.index(value)+1}/{len(cur_list)} \n"
        else:
            # YELLOW color for other types
            print_string += f"| {key:<30} | \033[93m{value:<30}\033[00m | {cur_list.index(value)+1}/{len(cur_list):<30} \n"



    print('\n'+print_string + '\n')

    [Method, run_type, start, goal,
            map_length,agent_count, experiment_iteration, min_rom_size] = scenario
    
    cfg = Config(scenario, parameters, debug=debug)

    random.seed(cfg.SEED)
    np.random.seed(cfg.SEED)

    Agent_Class_list = []

    experiment_name = f"{Method.__name__}/{run_type.__name__}/start-{start.__name__}/goal-{goal.__name__}/nbots-{cfg.N_BOTS}_map_length-{cfg.MAP_NP_ROWS}_min_room-{min_rom_size}_seed-{cfg.SEED}"


    Agent_Class_list = [type(Method.__name__+'_'+run_type.__name__, (Method, run_type,), {})] * cfg.N_BOTS

    search_method =''
    for i , name in enumerate(Agent_Class_list):
        search_method += experiment_name.replace("/", "\n") + '\n'

    # print("Method:\n", )
    # print("\033[92m" + search_method + "\033[0m")

    cur_experiment = Experiment(cfg, 
                    experiment_name, 
                    Agent_Class_list, 
                    search_method,
                    return_dict,
                    prosses_count,
                    start_method=start,
                    goal_method=goal,
                    debug=debug,
                    )

    return cur_experiment.run_experiment([None], )



def main(parameters = None):
    if  parameters == None:
        from parameters_cfg import Parameters
        parameters = Parameters()

    all_df = pd.DataFrame()
    process_manager = mp.Manager()
    return_dict = process_manager.dict()


    results = []

    all_scenarios =  itertools.product(*parameters.All_scenarios_dic.values())
    

    if parameters.Use_process:
        with mp.Pool(processes=int(mp.cpu_count()*0.90)) as pool:

            args = list({i:[scenario, parameters, return_dict, i, parameters.Debug] for i,scenario in  enumerate(all_scenarios)}.values())
            # Inspiration: https://stackoverflow.com/a/45276885/4856719
            results = list(tqdm.tqdm(pool.imap_unordered(run_scenario, args,)
                                    #  time shows hours, minutes, seconds
                                    , total=len(args), colour="MAGENTA", desc="⏰ Experiments Progress"))
    else:
        for i,scenario in  enumerate(tqdm.tqdm(itertools.product(*parameters.All_scenarios_dic.values()), colour="MAGENTA", desc="⏰ \033[95m Experiments Progress \033[95m", total=len(list(itertools.product(*parameters.All_scenarios_dic.values()))))):
            results.append(run_scenario([scenario, parameters, return_dict, i, parameters.Debug]))

    import time
    t_stamp = time.time()

    # parce the results
    for i, return_value in tqdm.tqdm( enumerate( results), colour="GREEN", desc="Saving Data", total=len(results)):
        try:    
            if return_value == None:
                print(f"🛑 Experiment {i} Failed cant save to df return: None: ", return_value)
                continue
            if len(return_value) != 2:
                print(f"🛑 Experiment {i} Failed cant save to df return was not len of 2", return_value)
                continue
            [df, cfg,] = return_value

            df['execution_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t_stamp))
            all_df = pd.concat([all_df, df], ignore_index=True)

        except Exception as e:
            print(f"🛑 Experiment {i} Failed cant save to df", e)
            continue

    # check if the data.csv file exists
    if os.path.isfile(f"data/all_data.csv"):
        # just read the file
        other_df = pd.read_csv(f"data/all_data.csv")

        # FIND THE LAST EXPERIMENT ID
        last_experiment_id = other_df['experiment_ID'].max()
        all_df["experiment_ID"] = all_df["experiment_ID"] + last_experiment_id + 1
        # append the new data to the end of the file
        all_df.to_csv(f"data/all_data.csv", mode='a', header=False)
    else:
        all_df.to_csv(f"data/all_data.csv")

if __name__ == "__main__":
    main()


