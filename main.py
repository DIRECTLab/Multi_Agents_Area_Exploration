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
    Sub_process_list = []
    cur_Method_list = Method_list.copy()
    cur_Method_list.remove("Heterogenus")
    assert len(cur_Method_list) > 1, "Heterogenus needs more than 1 method"

    print("\n\n")
    # get every combo of all the methods starting from 2 to the number of methods
    
    for combo in tqdm.tqdm(itertools.combinations(cur_Method_list, 2), desc=("\033[91m" + "Heterogenus"+ "\033[0m"), colour="YELLOW", total=len(list(itertools.combinations(cur_Method_list, 2)))):
        print(f"\n\n combo {len(combo)} {combo}")
        method1 = type(combo[0].__name__, (combo[0], start, goal), {})
        method2 = type(combo[1].__name__, (combo[1], start, goal), {})

        # ratio assinment of the agents
        for ratio in  tqdm.tqdm([(.50,.50), (.25,.75), (.75,.25)], desc="Ratio", colour="BLACK"):
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
            print("\033[92m" + search_method + "\033[0m")

            cur_experiment = Experiment(cfg, 
                            cur_experiment_name, 
                            Agent_Class_list, 
                            search_method,
                            return_dict,
                            prosses_count,
                            debug=debug,
                            )

            if cfg.USE_PROCESS:
                p = Process(target=cur_experiment.run_experiment, 
                            args=([None],))
                p.start()
                Sub_process_list.append(p)
                prosses_count += 1
            else:
                cur_experiment.run_experiment([None], )
                prosses_count += 1

        for p in tqdm.tqdm(Sub_process_list, desc="Joining Heterogenus Process", colour="RED"):
            p.join()
            print("Joined Process: ", p.pid)
        print()
            

def run_scenario(scenario, parameters, return_dict, prosses_count, p_bar, debug=False):
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
    cfg.CREATE_GIF = parameters.Create_gif
    cfg.USE_PROCESS = parameters.Use_process

    Agent_Class_list = []

    if Method == "Heterogenus":
        # remove the heterogenus from the list
        experiment_name = f"{Method}/"
        run_heterogenus(start, goal, cfg, experiment_name, return_dict, parameters.Method_list, prosses_count, debug = parameters.Debug)
        return

    experiment_name = f"{Method.__name__}/{run_type}/{start.__name__}/{goal.__name__}/nbots:{cfg.N_BOTS}_map_length:{cfg.ROWS}_seed:{cfg.SEED}"

    if Method == "DQN":
        Agent_Class_list = [Method]
    else:
        Agent_Class_list = [type(Method.__name__, (Method, start, goal), {})] * cfg.N_BOTS

    search_method =''
    for i , name in enumerate(Agent_Class_list):
        search_method += str(i) +' '+str(name).replace("<class '__main__.","").replace("'>","").replace(" ", "") + '\n'

    # print("Method:\n", )
    # print("\033[92m" + search_method + "\033[0m")

    cur_experiment = Experiment(cfg, 
                    experiment_name, 
                    Agent_Class_list, 
                    search_method,
                    return_dict,
                    prosses_count,
                    debug=debug,
                    )

    return_value = cur_experiment.run_experiment([None], )
    p_bar.update(1)
    # p_bar
    return return_value
    # if cfg.USE_PROCESS:
    #     p = Process(target=cur_experiment.run_experiment, 
    #                 args=([None],))
    #     p.start()
    #     return p
    # else:
    #     cur_experiment.run_experiment([None], )
    #     return None


def main(parameters = None):
    if  parameters == None:
        from parameters_cfg import Parameters
        parameters = Parameters()

    all_df = pd.DataFrame()
    process_manager = Manager()
    return_dict = process_manager.dict()
    Process_list = []
    # prosses_count = 1
    jobs_running = 0


    progress_bar = tqdm.tqdm(
            itertools.product(*parameters.All_scenarios_dic.values()),
                total=len(list(itertools.product(*parameters.All_scenarios_dic.values()))) , 
                colour="CYAN", desc="Experiments Progress")
    

    # for i,scenario in  enumerate(progress_bar):
    #     p_bar_desc = ""

    if parameters.Use_process:
        pool = Pool(processes=parameters.Max_process)

    results = []

    # setup progress bar
    progress_bar.set_description("Experiments Progress")
    progress_bar.set_postfix_str("")
    progress_bar.refresh()
    

    for prosses_count, scenario in enumerate( itertools.product(*parameters.All_scenarios_dic.values())):
        results.append(pool.apply_async(run_scenario, (scenario, parameters, return_dict, prosses_count, progress_bar, parameters.Debug, )))

    if parameters.Use_process:
        pool.close()
        pool.join()
  

    import time
    t_stamp = time.time()

    # parce the results
    for i, return_value in tqdm.tqdm( enumerate( results), colour="GREEN", desc="Saving Data", total=len(results)):
        [df, cfg,] = return_value.get()

        df['execution_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t_stamp))
        all_df = pd.concat([all_df, df], ignore_index=True)


    # if parameters.Use_process:
    #     for p in tqdm.tqdm(Process_list, desc="Joining Process", colour="RED"):
    #         p.join()
    #         print("Joined Process: ", p.pid)

    # Time stamp this data


    for i, [df, cfg] in tqdm.tqdm( enumerate(return_dict.values()), colour="GREEN", desc="Saving Data", total=len(return_dict.values())):
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
