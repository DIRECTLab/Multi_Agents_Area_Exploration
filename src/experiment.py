import matplotlib.pyplot as plt
import threading
from multiprocessing.pool import ThreadPool
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import psutil
import json
import numpy as np
import pandas as pd
import os
import time

import src.world as world
import src.agent as agent
import src.log_plot as log_plot
from src.darp.darp import *

#  related to our first voronoi calculation method
def generate_vor_cells_over_world(cfg):
    matrix_list, grid = list(), list()
    agent_locs = set()
    class Cell:
        def __init__(self, row, column):
            self.pos_row = row
            self.pos_column = column
            self.agent = False          # is there any agent over a cell
            self.agent_id = None        # which agent is placed on a box
            self.distance_matrix = None
        def calc_distance_matrices(self):
            x_arr, y_arr = np.mgrid[0:cfg.ROWS, 0:cfg.COLS]
            cell = (self.pos_row, self.pos_column)
            dists = np.sqrt((x_arr - cell[0])**2 + (y_arr - cell[1])**2)
            return dists
    for row in range(cfg.ROWS):
        grid.append([])
        for column in range(cfg.COLS):
            grid[row].append(Cell(row, column))
    return grid, matrix_list, agent_locs

#  related to our first voronoi calculation method
def generate_voronoi_division_grid(grid, bots, matrix_list, agent_locs, log_plot_obj):
    for i in range(len(bots)):
        column = bots[i].goal_xy[0]
        row = bots[i].goal_xy[1]
        grid[row][column].agent = True
        grid[row][column].agent_id = i
        grid[row][column].distance_matrix = grid[row][column].calc_distance_matrices()
        matrix_list.append(grid[row][column].distance_matrix)
        agent_locs.add((row, column))
        log_plot_obj.map_ax.scatter(x=column, y=row, c='r', s=100)
        log_plot_obj.map_ax.text(column, row, f"(x:{column},y:{row})", fontsize=10, color='g', ha='center', va='center')
    vor_region_over_grid = np.argmin((matrix_list), 0)
    return vor_region_over_grid


def setup_experiment(
                cfg,
                experiment_name,
                Agent_Class,
                search_method):
    
    if cfg.DRAW_SIM:
        # Initialize pygame
        pygame.init()
    else:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    # Define the size of the screen
    cur_world = world.World(cfg)
    # Generate the floor plan
    ground_truth_map = cur_world.generate_floor_plan()
    map_screen = cur_world.screen.copy()
    # cur_world.get_map(show_grid=True)
    minimum_comparison_table = None
    upscaling_down_sampled_map_for_vis = None

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
        log_plot_obj.map_ax.matshow(ground_truth_map)


    if cfg.DRAW_SIM:
        row = int(np.sqrt(cfg.N_BOTS))
        col = int(np.ceil(cfg.N_BOTS/row))
        bot_fig, bot_ax = plt.subplots(row, col, )#figsize=(10, 10))
        bot_fig.set_facecolor('gray')

        if cfg.N_BOTS == 1:
            bot_ax = [bot_ax]
        else:
            bot_ax = bot_ax.flatten()
        plt.ion()
    

    if 'Voronoi' in search_method:
        grid, matrix_list, agent_locs = generate_vor_cells_over_world(cfg)

        # Get the Starting Centroid for each agent
        # for centroid_xy in cfg.START_CENTROID_LIST_XY:
        #     column = centroid_xy[0]
        #     row = centroid_xy[1]
        #     # print(f"Bot {i} at x:{row}, y:{column}")
        #     grid[row][column].agent = True
        #     grid[row][column].agent_id = i
        #     grid[row][column].distance_matrix = grid[row][column].calc_distance_matrices()
        #     matrix_list.append(grid[row][column].distance_matrix)
        #     agent_locs.add((row,column))
        #     log_plot_obj.map_ax.scatter(x=column, y=row, c='r', s=100)
        #     log_plot_obj.map_ax.text(column, row, f"(x:{column},y:{row})", fontsize=10, color='g', ha='center', va='center')

    bots = []
    lock = threading.Lock()

    assert cfg.USE_THREADS != True, "The use of the threads is not enabled"
    
    for i in range(cfg.N_BOTS):
        bots.append(Agent_Class(
                    cfg = cfg,
                    id = i,
                    body_size = 3,
                    grid_size = cfg.GRID_THICKNESS,
                    lidar_range = ground_truth_map.shape[0]//6,
                    full_map = ground_truth_map,
                    ax = bot_ax[i] if cfg.DRAW_SIM else None,
                    screen = cur_world.screen if cfg.DRAW_SIM else None,
                    lock= lock,
                )
            )
    
        if cfg.DRAW_SIM:
            bot_ax[i].set_title(f"Bot {i}")
            bot_ax[i].matshow(bots[i].agent_map)

    if 'Voronoi' in search_method:
        minimum_comparison_table = generate_voronoi_division_grid(grid, bots, matrix_list, agent_locs, log_plot_obj)
        log_plot_obj.map_ax.matshow(minimum_comparison_table, alpha=0.6)
        # assign each robot one voronoi region using assigned_points
        for bot in bots:
            assigned_points = np.argwhere(minimum_comparison_table == bot.id)
            # convert list of list into list of tuples
            assigned_points = [tuple(point) for point in assigned_points]
            bot.assigned_points = assigned_points
            assert len(assigned_points) > 0, "No points assigned to bot"

    elif 'DarpVorOnly' in search_method:
        start_time = time.time()
        # agent_locations_rc = []
        goal_locations_rc = []
        for i in range(len(bots)):
            # agent_locations_rc.append((bots[i].grid_position_xy[0], bots[i].grid_position_xy[1]))
            goal_locations_rc.append((bots[i].goal_xy[1], bots[i].goal_xy[0]))
        # print("here is the agent locations...", agent_locations_rc)
        print("here is the goal locations1...", goal_locations_rc)


        # fig, ax = plt.subplots()
        # ax.matshow(ground_truth_map)
        # obstacle_locations = np.argwhere(down_sampled_map == False)

        obstacle_locations = np.argwhere(ground_truth_map == False)
        tuple_obst = tuple(map(tuple, obstacle_locations))

        # print("here are the obstacles...", tuple_obst)
        darp_instance = DARP(cfg.ROWS, cfg.COLS, goal_locations_rc, tuple_obst)

        darp_success , iterations = darp_instance.divideRegions()

        end_time = time.time()
        it_took = end_time - start_time
        print("total time it take to divide the map using darp:", it_took, "this many iterations:", iterations)

        for bot in bots:
            assigned_points = np.argwhere(darp_instance.A == bot.id)
            # convert list of list into list of tuples
            assigned_points = [tuple(point) for point in assigned_points]
            # new_four_points = []
            # for point in assigned_points:
            #     new_four_points.extend(((point[0]*2, point[1]*2), (point[0]*2, point[1]*2+1), (point[0]*2+1, point[1]*2), (point[0]*2+1, point[1]*2+1)))
            # bot.assigned_points = new_four_points
            bot.assigned_points = assigned_points
            assert len(assigned_points) > 0, "No points assigned to bot"
        
        upscaling_down_sampled_map_for_vis = darp_instance.A

    
    elif 'DarpMST' in search_method:
        start_time = time.time()
        agent_locations_rc = []
        for i in range(len(bots)):
            agent_locations_rc.append((bots[i].grid_position_xy[1]//2, bots[i].grid_position_xy[0]//2))
        print("here is the agent locations...", agent_locations_rc)
        
        
        # create a low resolution map by halving the size of the map
        # side a convolutional over the map and if any of the 4 pixels are occupied then the new pixel is occupied
        down_sampled_map = np.ones((ground_truth_map.shape[0]//2, ground_truth_map.shape[1]//2))
        for i in range(ground_truth_map.shape[0]//2):
            for j in range(ground_truth_map.shape[1]//2):
                convolution = ground_truth_map[2*i:2*i+2, 2*j:2*j+2]
                for cell in convolution:
                    if cfg.OBSTACLE in cell:
                        down_sampled_map[i][j] = cfg.OBSTACLE
                        break

        # add the doors back in to the down sampled map
        for door in cur_world.doors:
            if door[0] == 0 or door[1] == 0:
                continue
            door_x = int((door[0]/cfg.GRID_THICKNESS) //2)
            door_y = int((door[1]/cfg.GRID_THICKNESS) //2)
            down_sampled_map[door_y,door_x] = cfg.EMPTY

            # if horizontal door
            if door[2] > 0:
                down_sampled_map[door_y,door_x+1] = cfg.EMPTY
            # if vertical door
            else:
                down_sampled_map[door_y+1,door_x] = cfg.EMPTY

        # fig, ax = plt.subplots()
        # ax.matshow(down_sampled_map)
        obstacle_locations = np.argwhere(down_sampled_map == False)

        # obstacle_locations = np.argwhere(ground_truth_map == False)
        tuple_obst = tuple(map(tuple, obstacle_locations))

        # print("here are the obstacles...", tuple_obst)
        darp_instance = DARP(cfg.ROWS//2, cfg.COLS//2, agent_locations_rc, tuple_obst)

        darp_success , iterations = darp_instance.divideRegions()

        end_time = time.time()
        it_took = end_time - start_time

        upscaling_down_sampled_map_for_vis = np.zeros((cfg.ROWS, cfg.COLS))
        for i in range(len(darp_instance.A)):
            for j in range(len(darp_instance.A[0])):
                point = darp_instance.A[i][j]
                upscaling_down_sampled_map_for_vis[i*2, j*2] = point
                upscaling_down_sampled_map_for_vis[i*2, j*2+1] = point
                upscaling_down_sampled_map_for_vis[i*2+1, j*2] = point
                upscaling_down_sampled_map_for_vis[i*2+1, j*2+1] = point

        if darp_success:
            run_mst(iterations, bots, darp_instance)
            
        
    
    mutual_data = {}
    mutual_data['map'] = - np.ones((ground_truth_map.shape[0], ground_truth_map.shape[1])).astype(int)
    folder_name =  'data/' + experiment_name+ '/' + time.strftime("%Y-%m-%d_%H:%M:%S")
    if cfg.LOG_PLOTS:
        os.makedirs(folder_name)

        # log_plot_obj.plot_map(mutual_data, bots, data)
        log_plot_obj.map_ax.set_title(f"Max Known Area {ground_truth_map.size}\n {search_method} \n{experiment_name.replace('_',' ').title()}")
        if 'Voronoi' in search_method:
            log_plot_obj.map_ax.matshow(minimum_comparison_table, alpha=0.3)
        log_plot_obj.map_fig.savefig(folder_name + '/starting_map.png')

    if cfg.DRAW_SIM:
        bot_fig.savefig(folder_name + '/starting_bot.png')
    
    return [data, bots, ground_truth_map, mutual_data, log_plot_obj, minimum_comparison_table, cur_world, map_screen, folder_name, upscaling_down_sampled_map_for_vis]

def run_experiment(process_ID, 
                return_dict, 
                cfg, 
                experiment_name, 
                search_method,
                set_up_data,
                debug=False):

    [data, bots, ground_truth_map, mutual_data, log_plot_obj, 
            minimum_comparison_table, cur_world, map_screen, folder_name, upscaling_down_sampled_map_for_vis] = set_up_data
    if cfg.DRAW_SIM:
        # Display the floor plan on the screen
        pygame.display.update()
        FPS = 10
        clock = pygame.time.Clock()

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
            #     t = threading.Thread(target=bot.update, args=(mutual_data,cfg.DRAW_SIM ))
            #     t.start()
            #     theads.append(t)
                    
            pool = ThreadPool(processes=len(bots))
            for i, bot in enumerate(bots):
                # place each bot in a different thread
                t = pool.apply_async(bot.update, (mutual_data,cfg.DRAW_SIM ))
                threads.append(t)


            for i, (t, bot)  in enumerate(zip(threads,bots)):
                [length, dist] = t.get()
                path_length += length
            end_time = psutil.Process().cpu_times().user

        else:
            # time the bot update
            start_time = psutil.Process().cpu_times().user
            for i, bot in enumerate(bots):
                bot.update(mutual_data, draw=cfg.DRAW_SIM)
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
        cur_known = np.sum(mutual_data['map'] != -1)
        data['area_percent'].append(cur_known / mutual_data['map'].size)
        data['update_time'].append(end_time - start_time)
        data['delta_time'].append( psutil.Process().cpu_times().user - sim_start_time)
        data['plan_length'].append(path_length)
        data['replan_count'].append(replan_count)
        data['frame_count'].append(frame_count)
        data['known_area'].append(cur_known)

        if debug:
            if cfg.LOG_PLOTS:
                # update the ground_truth_map and plt
                log_plot_obj.plot_map(mutual_data['map'], bots, data)
                log_plot_obj.map_ax.set_title(f"Max Known Area {ground_truth_map.size}\n {search_method} \n{experiment_name.replace('_',' ').title()}")
                if 'Voronoi' in search_method :
                    log_plot_obj.map_ax.matshow(minimum_comparison_table, alpha=0.3)

                if "Darp" in search_method: #or "DarpVorOnly" in search_method:
                    log_plot_obj.map_ax.matshow(upscaling_down_sampled_map_for_vis, alpha=0.3)


            if cfg.DRAW_SIM or cfg.LOG_PLOTS:
                # update the ground_truth_map but continue 
                # wait to update plt at FPS of 10
                # if frame_count % 3 == 0:
                    # map_ax.matshow(mutual_data)
                plt.pause(0.00001)
                    # plt.pause(0.1)
                plt.draw()
        
        frame_count += 1
        if cur_known == mutual_data['map'].size:
            break

        logging_end_time = psutil.Process().cpu_times().user
        data['logging_time'].append(logging_end_time - logging_time_start)


    print(f"Simulation Complete: {experiment_name} in {data['delta_time'][-1]} seconds")
    
    # create expeament folder
    os.makedirs(f"{folder_name}", exist_ok=True)

    if cfg.LOG_PLOTS:
        # update the ground_truth_map and plt
        log_plot_obj.plot_map(mutual_data['map'], bots, data)
        log_plot_obj.map_ax.set_title(f"Max Known Area {ground_truth_map.size}")
        if 'Voronoi' in search_method:
            log_plot_obj.map_ax.matshow(minimum_comparison_table, alpha=0.3)

        log_plot_obj.map_fig.savefig(f"{folder_name}/map_fig.png")

    if cfg.DRAW_SIM:
        # save the screen
        pygame.image.save(cur_world.screen, f"{folder_name}/screen.png")
        pygame.quit()

    # save the config in jason format
    with open(f"{folder_name}/config.json", 'w') as f:
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
    df['wall_ratio'] = np.sum(ground_truth_map == 0) / ground_truth_map.size
    df['mathod'] = search_method

    df.to_csv(f"{folder_name}/data.csv")
    print(f"Done {experiment_name}")
    return_dict[process_ID] = [df, cfg, ground_truth_map]
    return df, cfg, ground_truth_map
