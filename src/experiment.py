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
from src.darp.kruskal import Kruskal
from src.darp.CalculateTrajectories import CalculateTrajectories
from src.darp.turns import turns
from src.darp.Visualization import visualize_paths

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

#  related to darp algorithm
def calculateMSTs(BinaryRobotRegions, droneNo, rows, cols, mode):
    MSTs = []
    for r in range(droneNo):
        k = Kruskal(rows, cols)
        k.initializeGraph(BinaryRobotRegions[r, :, :], True, mode)
        k.performKruskal()
        MSTs.append(k.mst)
    return MSTs

#  related to darp algorithm
def CalcRealBinaryReg(BinaryRobotRegion, rows, cols):
    temp = np.zeros((2*rows, 2*cols))
    RealBinaryRobotRegion = np.zeros((2 * rows, 2 * cols), dtype=bool)
    for i in range(2*rows):
        for j in range(2*cols):
            temp[i, j] = BinaryRobotRegion[(int(i / 2))][(int(j / 2))]
            if temp[i, j] == 0:
                RealBinaryRobotRegion[i, j] = False
            else:
                RealBinaryRobotRegion[i, j] = True
    return RealBinaryRobotRegion

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
    
    elif 'Darp' in search_method:
        start_time = time.time()
        agent_locations = []
        for i in range(len(bots)):
            column = bots[i].grid_position_xy[0]
            row = bots[i].grid_position_xy[1]
            agent_locations.append((column//2, row//2))
        print("here is the agent locations...", agent_locations)
        
        
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

        fig, ax = plt.subplots()
        ax.matshow(down_sampled_map)
        obstacle_locations = np.argwhere(down_sampled_map == False)

        # obstacle_locations = np.argwhere(ground_truth_map == False)
        tuple_obst = tuple(map(tuple, obstacle_locations))

        # print("here are the obstacles...", tuple_obst)
        darp_instance = DARP(cfg.ROWS//2, cfg.COLS//2, agent_locations, tuple_obst)

        darp_success , iterations = darp_instance.divideRegions()



        end_time = time.time()
        it_took = end_time - start_time
        if darp_success:
            print("Success...", "Iteration count is:", iterations, "\ncalculating this took:", it_took, "seconds...")
            # print("Agents", darp_instance.BinaryRobotRegions)
            # print("darp_instance.robotNumber", darp_instance.robotNumber)
            # print("darp_instance.rows", darp_instance.rows)
            # print("darp_instance.cols", darp_instance.cols)

            #  undo the convolutional by doubling the size of the map
            # for i in range(ground_truth_map.shape[0]//2):
            #     for j in range(ground_truth_map.shape[1]//2):
            #         convolution = ground_truth_map[2*i:2*i+2, 2*j:2*j+2]
            #         for cell in convolution:

            for bot in bots:
                assigned_points = np.argwhere(darp_instance.A == bot.id)
                # convert list of list into list of tuples
                assigned_points = [tuple(point) for point in assigned_points]
                bot.assigned_points = assigned_points
                assert len(assigned_points) > 0, "No points assigned to bot"

            mode_to_drone_turns = []
            AllRealPaths_dict = {}
            subCellsAssignment_dict = {}
            for mode in range(4):
                # print("mode", mode)
                MSTs = calculateMSTs(darp_instance.BinaryRobotRegions, darp_instance.robotNumber, darp_instance.rows, darp_instance.cols, mode)
                # print("MSTs", MSTs)
                
                
                AllRealPaths = []
                for r in range(darp_instance.robotNumber):
                    ct = CalculateTrajectories(darp_instance.rows, darp_instance.cols, MSTs[r])
                    ct.initializeGraph(CalcRealBinaryReg(darp_instance.BinaryRobotRegions[r], darp_instance.rows, darp_instance.cols), True)
                    ct.RemoveTheAppropriateEdges()
                    ct.CalculatePathsSequence(4 * darp_instance.initial_positions[r][0] * darp_instance.cols + 2 * darp_instance.initial_positions[r][1])
                    AllRealPaths.append(ct.PathSequence)
                # print("AllRealPaths", AllRealPaths)
                TypesOfLines = np.zeros((darp_instance.rows*2, darp_instance.cols*2, 2))
                

                for r in range(darp_instance.robotNumber):
                    flag = False
                    for connection in AllRealPaths[r]:
                        if flag:
                            if TypesOfLines[connection[0]][connection[1]][0] == 0:
                                indxadd1 = 0
                            else:
                                indxadd1 = 1

                            if TypesOfLines[connection[2]][connection[3]][0] == 0 and flag:
                                indxadd2 = 0
                            else:
                                indxadd2 = 1
                        else:
                            if not (TypesOfLines[connection[0]][connection[1]][0] == 0):
                                indxadd1 = 0
                            else:
                                indxadd1 = 1
                            if not (TypesOfLines[connection[2]][connection[3]][0] == 0 and flag):
                                indxadd2 = 0
                            else:
                                indxadd2 = 1

                        flag = True
                        if connection[0] == connection[2]:
                            if connection[1] > connection[3]:
                                TypesOfLines[connection[0]][connection[1]][indxadd1] = 2
                                TypesOfLines[connection[2]][connection[3]][indxadd2] = 3
                            else:
                                TypesOfLines[connection[0]][connection[1]][indxadd1] = 3
                                TypesOfLines[connection[2]][connection[3]][indxadd2] = 2

                        else:
                            if (connection[0] > connection[2]):
                                TypesOfLines[connection[0]][connection[1]][indxadd1] = 1
                                TypesOfLines[connection[2]][connection[3]][indxadd2] = 4
                            else:
                                TypesOfLines[connection[0]][connection[1]][indxadd1] = 4
                                TypesOfLines[connection[2]][connection[3]][indxadd2] = 1

                subCellsAssignment = np.zeros((2*darp_instance.rows, 2*darp_instance.cols))
                for i in range(darp_instance.rows):
                    for j in range(darp_instance.cols):
                        subCellsAssignment[2 * i][2 * j] = darp_instance.A[i][j]
                        subCellsAssignment[2 * i + 1][2 * j] = darp_instance.A[i][j]
                        subCellsAssignment[2 * i][2 * j + 1] = darp_instance.A[i][j]
                        subCellsAssignment[2 * i + 1][2 * j + 1] = darp_instance.A[i][j]

                drone_turns = turns(AllRealPaths)
                drone_turns.count_turns()
                drone_turns.find_avg_and_std()
                mode_to_drone_turns.append(drone_turns)

                AllRealPaths_dict[mode] = AllRealPaths
                subCellsAssignment_dict[mode] = subCellsAssignment


            # Find mode with the smaller number of turns
            averge_turns = [x.avg for x in mode_to_drone_turns]
            min_mode = averge_turns.index(min(averge_turns))
            
            # Retrieve number of cells per robot for the configuration with the smaller number of turns
            min_mode_num_paths = [len(x) for x in AllRealPaths_dict[min_mode]]
            min_mode_returnPaths = AllRealPaths_dict[min_mode]

            # Uncomment if you want to visualize all available modes
            # if self.darp_instance.visualization:
            #     for mode in range(4):
            #         image = visualize_paths(AllRealPaths_dict[mode], subCellsAssignment_dict[mode],
            #                                 self.darp_instance.droneNo, self.darp_instance.color)
            #         image.visualize_paths(mode)
            #     print("Best Mode:", self.min_mode)

            #Combine all modes to get one mode with the least available turns for each drone
            combined_modes_paths = []
            combined_modes_turns = []
            
            for r in range(darp_instance.robotNumber):
                min_turns = sys.maxsize
                temp_path = []
                for mode in range(4):
                    if mode_to_drone_turns[mode].turns[r] < min_turns:
                        temp_path = mode_to_drone_turns[mode].paths[r]
                        min_turns = mode_to_drone_turns[mode].turns[r]
                combined_modes_paths.append(temp_path)
                combined_modes_turns.append(min_turns)

            best_case = turns(combined_modes_paths)
            best_case.turns = combined_modes_turns
            best_case.find_avg_and_std()
            
            # Retrieve number of cells per robot for the best case configuration
            best_case_num_paths = [len(x) for x in best_case.paths]
            best_case_returnPaths = best_case.paths
            
            #visualize best case
            if darp_instance.visualization:
                image = visualize_paths(best_case.paths, subCellsAssignment_dict[min_mode],
                                        darp_instance.robotNumber, darp_instance.color)
                image.visualize_paths("Combined Modes")

            execution_time = time.time() - start_time
            
            print(f'\nResults:')
            print(f'Number of cells per robot: {best_case_num_paths}')
            print(f'Minimum number of cells in robots paths: {min(best_case_num_paths)}')
            print(f'Maximum number of cells in robots paths: {max(best_case_num_paths)}')
            print(f'Average number of cells in robots paths: {np.mean(np.array(best_case_num_paths))}')
            print(f'\nTurns Analysis: {best_case}')
            print(f'\nTime it take: {execution_time}')
        else:
            print("Problem occurred...")
    
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
    
    return [data, bots, ground_truth_map, mutual_data, log_plot_obj, minimum_comparison_table, cur_world, map_screen, folder_name]

def run_experiment(process_ID, 
                return_dict, 
                cfg, 
                experiment_name, 
                search_method,
                set_up_data,
                debug=False):

    [data, bots, ground_truth_map, mutual_data, log_plot_obj, 
            minimum_comparison_table, cur_world, map_screen, folder_name] = set_up_data
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
                if 'Voronoi' in search_method:
                    log_plot_obj.map_ax.matshow(minimum_comparison_table, alpha=0.3)

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
