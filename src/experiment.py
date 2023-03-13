import matplotlib.pyplot as plt
import threading
from multiprocessing.pool import ThreadPool

from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import psutil
from tqdm import tqdm
import json

import numpy as np
import pandas as pd


import src.world as world
import src.agent as agent
import src.log_plot as log_plot
from src.config import Config
import src.replan.voronoi_random as voronoi_random



def run_experiment(process_ID, return_dict, cfg, experiment_name, Search_methods):
    import os

    if cfg.DRAW_SIM:
        # Initialize pygame
        pygame.init()
    else:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    # Define the size of the screen
    cur_world = world.World(cfg)
    # Generate the floor plan
    map = cur_world.generate_floor_plan()
    map_screen = cur_world.screen.copy()
    # cur_world.get_map(show_grid=True)

    data= {
        'area_percent' : [],
        'update_time' : [],
        'delta_time' : [],
        'plan_length' : [],
        'replan_count' : [],
        'logging_time' : [0],
        'frame_count': [],
        'known_area' : [],
        }



    if cfg.LOG_PLOTS:
        # create Log_plot object
        log_plot_obj = log_plot.LogPlot(cfg, data)
        
        # space out the subplots
        log_plot_obj.map_fig.tight_layout()
        # create a grid of subplots 
        log_plot_obj.map_ax.matshow(map)


    if cfg.DRAW_SIM:
        row = int(np.sqrt(cfg.N_BOTS))
        col = int(np.ceil(cfg.N_BOTS/row))
        bot_fig, bot_ax = plt.subplots(row, col, )#figsize=(10, 10))

        if cfg.N_BOTS == 1:
            bot_ax = [bot_ax]
        else:
            bot_ax = bot_ax.flatten()
        plt.ion()
    
    if Search_methods['Use_Vernoi_method']:
        matrix_list, coming_set, colors, grid = list(), list(), list(), list()
        agent_locs = set()
        voronoi_random.ROWS = map.shape[0]
        voronoi_random.COLUMNS = map.shape[1]




    for row in range(cfg.ROWS):
        grid.append([])
        for column in range(cfg.COLS):
            grid[row].append(voronoi_random.Cell(row,column))
    
    bots = []
    lock = threading.Lock()

        
    assert cfg.USE_THREADS != True, "The use of the threads is not enabled"

    for i in range(cfg.N_BOTS):
        bots.append(agent.Agent(
                    cfg = cfg,
                    id = i,
                    body_size = 3,
                    grid_size = cfg.GRID_THICKNESS,
                    lidar_range = map.shape[0]//3,
                    full_map = map,
                    ax = bot_ax[i] if cfg.DRAW_SIM else None,
                    screen = cur_world.screen if cfg.DRAW_SIM else None,
                    lock= lock,
                )
            )
        
        if Search_methods['Use_Vernoi_method']:
            column = bots[i].grid_position_xy[0]
            row = bots[i].grid_position_xy[1]
            # print(f"Bot {i} at x:{row}, y:{column}")

            grid[row][column].agent = True
            grid[row][column].agent_id = i
            grid[row][column].distance_matrix = grid[row][column].calc_distance_matrices()
            matrix_list.append(grid[row][column].distance_matrix)
            agent_locs.add((row,column))
            log_plot_obj.map_ax.scatter(x=column, y=row, c='r', s=100)
            log_plot_obj.map_ax.text(column, row, f"(x:{column},y:{row})", fontsize=10, color='g', ha='center', va='center')


        if cfg.DRAW_SIM:
            bot_ax[i].set_title(f"Bot {i}")
            bot_ax[i].matshow(bots[i].agent_map)

    if Search_methods['Use_Vernoi_method']:
        minimum_comparison_table = np.argmin((matrix_list), 0)
        log_plot_obj.map_ax.matshow(minimum_comparison_table, alpha=0.6)
        for bot in bots:
            assigned_points = np.argwhere(minimum_comparison_table == bot.id)
            # convert list of list into list of tuples
            assigned_points = [tuple(point) for point in assigned_points]
            bot.assigned_points = assigned_points



    if cfg.DRAW_SIM:        
        # Display the floor plan on the screen
        pygame.display.update()
        FPS = 10
        clock = pygame.time.Clock()

    
    mutual_map = - np.ones((map.shape[0], map.shape[1])).astype(int)

    # Wait for the user to close the window
    frame_count = 0
    sim_start_time = psutil.Process().cpu_times().user
    while True:
        path_length = 0
        replan_count = 0
        if cfg.USE_THREADS:
            threads = []
            start_time = psutil.Process().cpu_times().user
            # for bot in bots:
            #     # place each bot in a different thread
            #     t = threading.Thread(target=bot.update, args=(mutual_map,cfg.DRAW_SIM ))
            #     t.start()
            #     theads.append(t)
                    
            pool = ThreadPool(processes=len(bots))
            for i, bot in enumerate(bots):
                # place each bot in a different thread
                t = pool.apply_async(bot.update, (mutual_map,cfg.DRAW_SIM ))
                threads.append(t)


            for i, (t, bot)  in enumerate(zip(threads,bots)):
                [length, dist] = t.get()
                path_length += length
            end_time = psutil.Process().cpu_times().user

        else:
            # time the bot update
            start_time = psutil.Process().cpu_times().user
            for i, bot in enumerate(bots):
                bot.update(mutual_map, draw=cfg.DRAW_SIM)
                path_length += len(bot.plan)
                replan_count += bot.replan_count
            end_time = psutil.Process().cpu_times().user



        if cfg.DRAW_SIM:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            clock.tick(FPS)
            # update the scrren
            pygame.display.update()
            cur_world.screen.blit(map_screen, (0, 0))
            print("clock.get_fps()",clock.get_fps(), end='\r')

        # LOG ALL THE DATA
        logging_time_start = psutil.Process().cpu_times().user
        cur_known = np.sum(mutual_map != -1)
        data['area_percent'].append(cur_known / mutual_map.size)
        data['update_time'].append(end_time - start_time)
        data['delta_time'].append( psutil.Process().cpu_times().user - sim_start_time)
        data['plan_length'].append(path_length)
        data['replan_count'].append(replan_count)
        data['frame_count'].append(frame_count)
        data['known_area'].append(cur_known)

        if cfg.LOG_PLOTS:
            # update the map and plt
            log_plot_obj.plot_map(mutual_map, bots, data)
            log_plot_obj.map_ax.set_title(f"Max Known Area {map.size}")
            if Search_methods['Use_Vernoi_method']:
                log_plot_obj.map_ax.matshow(minimum_comparison_table, alpha=0.3)

        if cfg.DRAW_SIM or cfg.LOG_PLOTS:
            # update the map but continue 
            # wait to update plt at FPS of 10
            # if frame_count % 3 == 0:
                # map_ax.matshow(mutual_map)
                # plt.pause(0.00001)
            plt.pause(0.0001)
                # plt.pause(0.1)
            plt.draw()
        
        frame_count += 1
        if cur_known == mutual_map.size:
            break

        logging_end_time = psutil.Process().cpu_times().user
        data['logging_time'].append(logging_end_time - logging_time_start)


    print(f"Simulation Complete: {experiment_name} in {data['delta_time'][-1]} seconds")
    import time
    import os
    folder_name =  experiment_name+ '/' + time.strftime("%Y-%m-%d_%H:%M:%S")
    # create expeament folder
    os.makedirs(f"data/{folder_name}", exist_ok=True)

    if cfg.LOG_PLOTS:
        # update the map and plt
        log_plot_obj.plot_map(mutual_map, bots, data)
        log_plot_obj.map_ax.set_title(f"Max Known Area {map.size}")
        if Search_methods['Use_Vernoi_method']:
            log_plot_obj.map_ax.matshow(minimum_comparison_table, alpha=0.3)

        log_plot_obj.map_fig.savefig(f"data/{folder_name}/map_fig.png")

    if cfg.DRAW_SIM:
        # save the screen
        pygame.image.save(cur_world.screen, f"data/{folder_name}/screen.png")
        pygame.quit()

    # save the config in jason format
    with open(f"data/{folder_name}/config.json", 'w') as f:
        json.dump(cfg.__dict__, f, indent=4)


    # save the data
    df = pd.DataFrame(data)
    # add the config to the data frame
    df['SEED'.lower()] = cfg.SEED 
    df['DRAW_SIM'.lower()] = cfg.DRAW_SIM
    df['LOG_PLOTS'.lower()] = cfg.LOG_PLOTS
    df['USE_THREADS'.lower()] = cfg.USE_THREADS
    df['N_BOTS'.lower()] = cfg.N_BOTS
    df['GRID_THICKNESS'.lower()] = cfg.GRID_THICKNESS
    df['SCREEN_WIDTH'.lower()] = cfg.SCREEN_WIDTH
    df['SCREEN_HEIGHT'.lower()] = cfg.SCREEN_HEIGHT
    df['MIN_ROOM_SIZE'.lower()] = cfg.MIN_ROOM_SIZE 
    df['MAX_ROOM_SIZE'.lower()] = cfg.MAX_ROOM_SIZE
    # area densely
    df['wall_ratio'] = np.sum(map == 0) / map.size

    df.to_csv(f"data/{folder_name}/data.csv")
    print(f"Done {experiment_name}")
    return_dict[process_ID] = [df, cfg, map]
    return df, cfg, map
