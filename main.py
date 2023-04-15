import random
import numpy as np
import pandas as pd
import os
from multiprocessing import Pool, Manager, Process, Queue

from src.experiment import *
from src.config import Config



import itertools
import tqdm

def run_heterogenus(start, goal, cfg, experiment_name, return_dict, Method_list, prosses_count, debug=False):
    cur_Method_list = Method_list.copy()
    cur_Method_list.remove("Heterogenus")
    assert len(cur_Method_list) > 1, "Heterogenus needs more than 1 method"

    print("\n\n")
    # get every combo of all the methods starting from 2 to the number of methods
    
    for combo in tqdm.tqdm(itertools.combinations(cur_Method_list, 2), desc="Heterogenus", colour="YELLOW"):
        print(f"combo {len(combo)} {combo}")
        method1 = type(combo[0].__name__, (combo[0], start, goal), {})
        method2 = type(combo[1].__name__, (combo[1], start, goal), {})

        # ratio assinment of the agents
        for ratio in  tqdm.tqdm([(.50,.50), (.25,.75), (.75,.25)], desc="Ratio", colour="GREEN"):
            method1_couint =  int(cfg.N_BOTS * ratio[0]) # % of the agents
            method2_couint =  int(cfg.N_BOTS * ratio[1])
            cur_experiment_name = experiment_name + f"method1:{method1.__name__}_count:{method1_couint}\nmethod2:{method2.__name__}_count:{method2_couint}/" 
            cur_experiment_name += f'\nnbots:{cfg.N_BOTS}_map_length:{cfg.ROWS}_seed:{cfg.SEED}'

            Agent_Class_list = [method1] * method1_couint
            Agent_Class_list += [method2] * method2_couint

            search_method =''
            for i , name in enumerate(Agent_Class_list):
                search_method += str(i) +' '+str(name).replace("<class '__main__.","").replace("'>","").replace(" ", "") + '\n'

            print("Method:\n", )
            prGreen(search_method)
            cur_experiment = Experiment(cfg, 
                            cur_experiment_name, 
                            Agent_Class_list, 
                            search_method,
                            return_dict,
                            prosses_count,
                            debug=debug,
                            )

            cur_experiment.run_experiment([None], )
            prosses_count += 1
            
    return return_dict


def main(parameters = None):
    if  parameters == None:
        from parameters_cfg import Parameters
        parameters = Parameters()

    all_df = pd.DataFrame()
    df_index = 0
    
    process_manager = Manager()
    return_dict = process_manager.dict()
    Process_list = []
    DEBUG = parameters.Debug
    USE_PROCESS = parameters.Use_process

    assert not (DEBUG and USE_PROCESS), "Can't use process and debug at the same time"
    prosses_count = 1


    progress_bar = tqdm.tqdm(
            itertools.product(*parameters.All_scenarios_dic.values()),
                total=len(list(itertools.product(*parameters.All_scenarios_dic.values()))) , 
                colour="CYAN", desc="Experiments Progress")
    

    for i,scenario in  enumerate(progress_bar):
        p_bar_desc = ""
        print_string =""
        for i, [key,value, cur_list] in enumerate(zip(parameters.All_scenarios_dic.keys(), scenario, parameters.All_scenarios_dic.values())):
            cur_list = list(cur_list)
            if type(value ) ==type:
                #GREEN color
                print_string += f"| {key:<30} | \033[92m{value.__name__:<30}\033[00m | {cur_list.index(value)+1}/{len(cur_list)} \n"
            else:
                #YELLOW color
                print_string += f"| {key:<30} | \033[93m{value:<30}\033[00m | {cur_list.index(value)+1}/{len(cur_list):<30} \n"


        print('\n'+print_string + '\n')

        [Method, run_type, start, goal,
            map_length,agent_count, experiment_iteration] = scenario
        
        cfg = Config()
        cfg.SEED = int(map_length + experiment_iteration)
        cfg.N_BOTS = int(agent_count)
        cfg.ROBOT_LOSS_TYPE = run_type

        random.seed(cfg.SEED)
        np.random.seed(cfg.SEED)

        cfg.COLS = int(map_length)
        cfg.ROWS = int(map_length)
        cfg.SCREEN_WIDTH = int(map_length*cfg.GRID_THICKNESS)
        cfg.SCREEN_HEIGHT = int(map_length*cfg.GRID_THICKNESS)

        Agent_Class_list = []

        if Method == "Heterogenus":
            # remove the heterogenus from the list
            experiment_name = f"{Method}/"
            run_heterogenus(start, goal, cfg, experiment_name, return_dict, parameters.Method_list, prosses_count, debug =DEBUG)
            continue

        experiment_name = f"{Method.__name__}/{run_type}/{start.__name__}/{goal.__name__}/nbots-{cfg.N_BOTS}_length-{cfg.COLS}_seed-{cfg.SEED}"
        print(f"Starting Experiment: {experiment_name}")
        Agent_Class = type(Method.__name__, (Method, start, goal), {})
        search_method =''.join(str(base.__name__)+'\n'  for base in Agent_Class.__bases__)
        search_method += Agent_Class.__name__
        print("Method:", search_method)
        Agent_Class_list = [Agent_Class] * cfg.N_BOTS

        cur_experiment = Experiment(cfg, 
                                    experiment_name, 
                                    Agent_Class_list, 
                                    search_method,
                                    return_dict,
                                    prosses_count,
                                    debug=DEBUG,
                                    )
        if USE_PROCESS:
            # run the simulation in a new process
            p = Process(target=cur_experiment.run_experiment, 
                        args=([None],))
            p.start()
            Process_list.append(p)
            prosses_count += 1
        else:
            cur_experiment.run_experiment([None], )
            prosses_count += 1



    if USE_PROCESS:
        for p in Process_list:
            p.join()
            print("Joined Process: ", p.pid)

    # Time stamp this data
    import time
    t_stamp = time.time()

    for i, [df, cfg, full_map] in enumerate(return_dict.values()):
        # all_df = all_df.append(df, ignore_index=True)
        # concat the dataframes
        df['execution_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t_stamp))
        all_df = pd.concat([all_df, df], ignore_index=True)

    # check if the data.csv file exists
    if os.path.isfile(f"data/all_data.csv"):
        # append the new data to the end of the file
        all_df.to_csv(f"data/all_data.csv", mode='a', header=False)
    else:
        all_df.to_csv(f"data/all_data.csv")

if __name__ == "__main__":
    main()
    # save the Conda environment yaml file so that we can recreate the environment on any machine
    import os
    # with out the prefix, the environment will be saved to the current directory
    os.system("conda env export --no-builds > environment.yml")
