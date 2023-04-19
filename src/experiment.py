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
import tqdm

import src.world as world
import src.agent as agent
import src.log_plot as log_plot
from src.darp.darp import *
import traceback
import sys

def downsampled_empty_point(point, downsampled_map, cfg):
    point = point
    # choose a fandome point from the 8 neighbors
    neighbors = [(point[0]+1, point[1]), \
                (point[0]-1, point[1]), \
                (point[0], point[1]+1), \
                (point[0], point[1]-1), \
                (point[0]+1, point[1]+1), \
                (point[0]-1, point[1]+1), \
                (point[0]+1, point[1]-1), \
                (point[0]-1, point[1]-1)]

    
    # shuffle the neighbors
    np.random.shuffle(neighbors)
    for cur_point in neighbors:
        # check if the point is in the map
        if cur_point[0] < 0 or cur_point[0] >= cfg.COLS//2 or \
            cur_point[1] < 0 or cur_point[1] >= cfg.ROWS//2:
            continue
        if downsampled_map[cur_point[1], cur_point[0]] == cfg.EMPTY:
            point = cur_point
            return point
    return False

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


class Experiment:
    def __init__(self, cfg, 
                experiment_name,
                Agent_Class_list,
                search_method, 
                return_dict,
                process_ID,
                debug=False,
                figs=[]):
        self.cfg = cfg
        self.experiment_name = experiment_name
        self.Agent_Class_list = Agent_Class_list
        self.search_method = search_method
        self.return_dict = return_dict
        self.debug = debug
        self.experiment_ID = process_ID

        if cfg.DRAW_SIM:
            # Initialize pygame
            pygame.init()
        else:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        
        # Set the random seed for reproducibility
        random.seed(cfg.SEED)
        np.random.seed(cfg.SEED)
        # Define the size of the screen
        self.cur_world = world.World(cfg)
        # Generate the floor plan
        self.ground_truth_map = self.cur_world.generate_floor_plan()
        self.map_screen = self.cur_world.screen.copy()
        # cur_world.get_map(show_grid=True)
        self.minimum_comparison_table = None
        self.upscaling_down_sampled_map_for_vis = None

        self.data= {
            'area_percent' : [],
            'update_time' : [],
            'delta_time' : [],
            'plan_length' : [],
            'replan_count' : [],
            'logging_time' : [0],
            }
        non_plot_data ={
            'frame_count': [],
            'known_area' : [],
            }
        
        if 'Epsilon' in search_method:
            for i, agent in enumerate(self.Agent_Class_list):
                if 'Epsilon' in agent.__name__:
                    self.data[f'epsilon_{i}'] = []
            

        if cfg.LOG_PLOTS:
            # create Log_plot object
            if figs == []:
                self.log_plot_obj = log_plot.LogPlot(cfg, self.data)
            else:
                self.log_plot_obj = log_plot.LogPlot(cfg, self.data, map_fig=figs[0], plot_fig=figs[1])
            # space out the subplots
            # self.log_plot_obj.map_fig.tight_layout()
            # create a grid of subplots 
            self.log_plot_obj.map_ax.matshow(self.ground_truth_map)

        # add non_plot_data to data
        self.data = {**self.data, **non_plot_data}

        if cfg.DRAW_SIM:
            row = int(np.sqrt(cfg.N_BOTS))
            col = int(np.ceil(cfg.N_BOTS/row))
            bot_fig, bot_ax = plt.subplots(row, col, )#figsize=(10, 10))
            bot_fig.set_facecolor('gray')

            if cfg.N_BOTS == 1:
                bot_ax = [bot_ax]
            else:
                bot_ax = bot_ax.flatten()
            # plt.ion()
        

        if 'Voronoi' in search_method:
            grid, matrix_list, agent_locs = generate_vor_cells_over_world(cfg)


        self.bots = []
        self.lock = threading.Lock()

        assert cfg.USE_THREADS != True, "The use of the threads is not enabled"
        
        # Agent_Class_list
        for i, agent_class in enumerate(Agent_Class_list):
            self.bots.append(agent_class(
                        cfg = cfg,
                        id = i,
                        body_size = 3,
                        grid_size = cfg.GRID_THICKNESS,
                        lidar_range = self.ground_truth_map.shape[0]//6,
                        full_map = self.ground_truth_map,
                        ax = bot_ax[i] if cfg.DRAW_SIM else None,
                        screen = self.cur_world.screen if cfg.DRAW_SIM else None,
                        lock= self.lock,
                    )
                )
            self.ground_truth_map[self.bots[-1].goal_xy[1]][self.bots[-1].goal_xy[0]] =cfg.AGENT_OBSTACLE
        
            if cfg.DRAW_SIM:
                bot_ax[i].set_title(f"Bot {i}")
                bot_ax[i].matshow(self.bots[i].agent_map)

        if 'Voronoi' in search_method:
            self.minimum_comparison_table = generate_voronoi_division_grid(grid, self.bots, matrix_list, agent_locs, self.log_plot_obj)
            self.log_plot_obj.map_ax.matshow(self.minimum_comparison_table, alpha=0.6)
            # assign each robot one voronoi region using assigned_points
            for bot in self.bots:
                assigned_points = np.argwhere(self.minimum_comparison_table == bot.id)
                # convert list of list into list of tuples
                assigned_points = [tuple(point) for point in assigned_points]
                bot.assigned_points = assigned_points
                assert len(assigned_points) > 0, "No points assigned to bot"

        elif 'DarpVorOnly' in search_method:
            start_time = time.time()
            # agent_locations_rc = []
            goal_locations_rc = []
            for i in range(len(self.bots)):
                # agent_locations_rc.append((bots[i].grid_position_xy[0], bots[i].grid_position_xy[1]))
                goal_locations_rc.append((self.bots[i].goal_xy[1], self.bots[i].goal_xy[0]))
            # print("here is the agent locations...", agent_locations_rc)
            print("here is the goal locations1...", goal_locations_rc)


            # fig, ax = plt.subplots()
            # ax.matshow(ground_truth_map)
            # obstacle_locations = np.argwhere(down_sampled_map == False)

            obstacle_locations = np.argwhere(self.ground_truth_map == False)
            tuple_obst_rc = tuple(map(tuple, obstacle_locations))

            # print("here are the obstacles...", tuple_obst)
            darp_instance = DARP(cfg.ROWS, cfg.COLS, goal_locations_rc, tuple_obst_rc)

            darp_success , iterations = darp_instance.divideRegions()

            end_time = time.time()
            it_took = end_time - start_time
            print("total time it take to divide the map using darp:", it_took, "this many iterations:", iterations)

            for bot in self.bots:
                assigned_points = np.argwhere(darp_instance.A == bot.id)
                # convert list of list into list of tuples
                assigned_points = [tuple(point) for point in assigned_points]
                # new_four_points = []
                # for point in assigned_points:
                #     new_four_points.extend(((point[0]*2, point[1]*2), (point[0]*2, point[1]*2+1), (point[0]*2+1, point[1]*2), (point[0]*2+1, point[1]*2+1)))
                # bot.assigned_points = new_four_points
                bot.assigned_points = assigned_points
                assert len(assigned_points) > 0, "No points assigned to bot"
            
            self.upscaling_down_sampled_map_for_vis = darp_instance.A

        
        elif 'DarpMST' in search_method:
            start_time = time.time()
            
            # create a low resolution map by halving the size of the map
            # side a convolutional over the map and if any of the 4 pixels are occupied then the new pixel is occupied
            down_sampled_map = np.ones((self.ground_truth_map.shape[0]//2, self.ground_truth_map.shape[1]//2))
            for i in range(self.ground_truth_map.shape[0]//2):
                for j in range(self.ground_truth_map.shape[1]//2):
                    convolution = self.ground_truth_map[2*i:2*i+2, 2*j:2*j+2]
                    for cell in convolution:
                        if cfg.OBSTACLE in cell:
                            down_sampled_map[i][j] = cfg.OBSTACLE
                            break

            # add the doors back in to the down sampled map
            for door in self.cur_world.doors:
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
            tuple_obst_rc = tuple(map(tuple, obstacle_locations))
            

            agent_locations_xy = []
            plt.matshow(down_sampled_map)
            for i in range(len(self.bots)):
                if (self.bots[i].grid_position_xy[1]//2, self.bots[i].grid_position_xy[0]//2) not in tuple_obst_rc:
                    # print("heyy")
                    agent_locations_xy.append((self.bots[i].grid_position_xy[1]//2, self.bots[i].grid_position_xy[0]//2))
                else:
                    # print("**********",self.bots[i].grid_position_xy[0]//2, self.bots[i].grid_position_xy[1]//2)
                    new_point = downsampled_empty_point((self.bots[i].grid_position_xy[1]//2, self.bots[i].grid_position_xy[0]//2), down_sampled_map, cfg)
                    # print("*****new point", new_point)
                    agent_locations_xy.append(new_point)
                self.log_plot_obj.draw_bots(self.bots)
                plt.scatter(agent_locations_xy[i][1], agent_locations_xy[i][0], c='r')
            
                

            print("here is the finalized agent locations...", agent_locations_xy)

            # print("here are the obstacles...", tuple_obst)
            darp_instance = DARP(cfg.ROWS//2, cfg.COLS//2, agent_locations_xy, tuple_obst_rc)

            darp_success , iterations = darp_instance.divideRegions()

            end_time = time.time()
            it_took = end_time - start_time

            self.upscaling_down_sampled_map_for_vis = np.zeros((cfg.ROWS, cfg.COLS))
            for i in range(len(darp_instance.A)):
                for j in range(len(darp_instance.A[0])):
                    point = darp_instance.A[i][j]
                    self.upscaling_down_sampled_map_for_vis[i*2, j*2] = point
                    self.upscaling_down_sampled_map_for_vis[i*2, j*2+1] = point
                    self.upscaling_down_sampled_map_for_vis[i*2+1, j*2] = point
                    self.upscaling_down_sampled_map_for_vis[i*2+1, j*2+1] = point

            if darp_success:
                run_mst(iterations, self.bots, darp_instance)
            else:
                print("DARP failed to find a solution")
                sys.exit()

                
            
        self.frame_count = 0
        self.mutual_data = {}
        self.mutual_data['map'] = - np.ones((self.ground_truth_map.shape[0], self.ground_truth_map.shape[1])).astype(int)
        self.folder_name =  'data/' + experiment_name+ '/' + time.strftime("%Y-%m-%d_%H-%M-%S")
        if cfg.LOG_PLOTS:
            os.makedirs(self.folder_name)

            # self.log_plot_obj.plot_map(mutual_data, bots, data)
            self.log_plot_obj.map_ax.set_title(f"Max Known Area {self.ground_truth_map.size} \n {search_method}")
            # ensure the Title is not cut off
            # self.log_plot_obj.map_fig.tight_layout()
            if 'Voronoi' in search_method:
                self.log_plot_obj.map_ax.matshow(self.minimum_comparison_table, alpha=0.3)
            self.log_plot_obj.map_fig.savefig(self.folder_name + '/starting_map.png')

        if cfg.DRAW_SIM:
            bot_fig.savefig(self.folder_name + '/starting_bot.png')
    
    # return [data, bots, ground_truth_map, mutual_data, self.log_plot_obj, self.minimum_comparison_table, cur_world, map_screen, self.folder_name, upscaling_down_sampled_map_for_vis]
    
    def setup_run_now(self):
        if self.cfg.DRAW_SIM:
            # Display the floor plan on the screen
            pygame.display.update()
            FPS = 10
            clock = pygame.time.Clock()

        # Wait for the user to close the window
        self.frame_count = 0
        self.sim_start_time = psutil.Process().cpu_times().user


    def clean_up_experiment(self):
            
        
        # create expeament folder
        os.makedirs(f"{self.folder_name}", exist_ok=True)

        if self.cfg.LOG_PLOTS:
            # update the ground_truth_map and plt
            self.log_plot_obj.plot_map(self.mutual_data['map'], self.bots, self.data)
            self.log_plot_obj.map_ax.set_title(f"Max Known Area {self.ground_truth_map.size}")
            if 'Voronoi' in self.search_method:
                self.log_plot_obj.map_ax.matshow(self.minimum_comparison_table, alpha=0.3)

            self.log_plot_obj.map_fig.savefig(f"{self.folder_name}/map_fig.png")

        if self.cfg.DRAW_SIM:
            # save the screen
            pygame.image.save(self.cur_world.screen, f"{self.folder_name}/screen.png")
            pygame.quit()

        # save the config in jason format
        with open(f"{self.folder_name}/config.json", 'w') as f:
            json.dump(self.cfg.__dict__, f, indent=4)


        # save the data
        df = pd.DataFrame(self.data)
        # add the config to the data frame
        df['SEED'.lower()] = self.cfg.SEED 
        df['DRAW_SIM'.lower()] = self.cfg.DRAW_SIM
        df['LOG_PLOTS'.lower()] = self.cfg.LOG_PLOTS
        df['USE_THREADS'.lower()] = self.cfg.USE_THREADS
        df['N_BOTS'.lower()] = self.cfg.N_BOTS
        df['GRID_THICKNESS'.lower()] = self.cfg.GRID_THICKNESS
        df['SCREEN_WIDTH'.lower()] = self.cfg.SCREEN_WIDTH
        df['SCREEN_HEIGHT'.lower()] = self.cfg.SCREEN_HEIGHT
        df['MIN_ROOM_SIZE'.lower()] = self.cfg.MIN_ROOM_SIZE 
        df['MAX_ROOM_SIZE'.lower()] = self.cfg.MAX_ROOM_SIZE
        # area densely
        df['wall_ratio'] = np.sum(self.ground_truth_map == 0) / self.ground_truth_map.size
        df['method'] = self.experiment_name.split('/')[0]
        df['start_scenario'] = self.experiment_name.split('/')[2]
        df['goal_scenario'] = self.experiment_name.split('/')[3]
        df['experiment_ID'] = self.experiment_ID
        df['loss_type'] = self.cfg.ROBOT_LOSS_TYPE

        df.to_csv(f"{self.folder_name}/data.csv")
        self.return_dict[self.experiment_ID] = [df, self.cfg, self.ground_truth_map]

        # close all plots
        plt.close('all')

        if self.cfg.CREATE_GIF:
            self.make_gif(self.folder_name)
        
        return df, self.cfg


    def render(self):
        if self.cfg.DRAW_SIM:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            self.clock.tick(self.FPS)
            # update the scrren
            pygame.display.update()
            self.cur_world.screen.blit(self.map_screen, (0, 0))
            print("clock.get_fps()",self.clock.get_fps(), end='\r')

        if self.cfg.LOG_PLOTS:
            # update the ground_truth_map and plt
            self.log_plot_obj.plot_map(self.mutual_data['map'], self.bots, self.data)

            tittle = (self.experiment_name).replace("/", "\n").replace('_',' ').title() + f"\nMax Known Area {self.ground_truth_map.size}"
            self.log_plot_obj.map_ax.set_title(tittle)
            if 'Voronoi' in self.search_method :
                self.log_plot_obj.map_ax.matshow(self.minimum_comparison_table, alpha=0.3)

            if "Darp" in self.search_method: #or "DarpVorOnly" in search_method:
                self.log_plot_obj.map_ax.matshow(self.upscaling_down_sampled_map_for_vis, alpha=0.3)


        if self.cfg.DRAW_SIM or self.cfg.LOG_PLOTS:
            # update the ground_truth_map but continue 
            # wait to update plt at FPS of 10
            # if frame_count % 3 == 0:
                # map_ax.matshow(mutual_data)
            plt.pause(0.00001)
                # plt.pause(0.1)
            plt.draw()

    def spawn_update_thread(self):
        threads = []
        start_time = psutil.Process().cpu_times().user
        pool = ThreadPool(processes=len(self.bots))
        for i, bot in enumerate(self.bots):
            # place each bot in a different thread
            t = pool.apply_async(bot.update, (self.mutual_data,self.cfg.DRAW_SIM ))
            threads.append(t)
        for i, (t, bot)  in enumerate(zip(threads,self.bots)):
            [length, dist] = t.get()
            path_length += length


    def env_step(self):
        # This is the main loop of the simulation
        path_length = 0
        replan_count = 0
        if self.cfg.USE_THREADS:
            self.spawn_update_thread()
            end_time = psutil.Process().cpu_times().user
        else:
            # time the bot update
            start_time = psutil.Process().cpu_times().user
            for i, bot in enumerate(self.bots):
                bot.update(self.mutual_data, draw=self.cfg.DRAW_SIM)
                bot.frame_count =self.frame_count
                path_length += len(bot.plan if bot.plan is not None else [])
                replan_count += bot.replan_count
                if 'Epsilon' in self.search_method and dir(bot).count('epsilon'):
                
                    self.data['epsilon_'+str(bot.id)].append(bot.epsilon)

            end_time = psutil.Process().cpu_times().user

        # LOG ALL THE DATA
        logging_time_start = psutil.Process().cpu_times().user
        cur_known = np.sum(self.mutual_data['map'] != -1)
        self.data['area_percent'].append(cur_known / self.mutual_data['map'].size)
        self.data['update_time'].append(end_time - start_time)
        self.data['delta_time'].append( psutil.Process().cpu_times().user - self.sim_start_time)
        self.data['plan_length'].append(path_length)
        self.data['replan_count'].append(replan_count)
        self.data['frame_count'].append(self.frame_count)
        self.data['known_area'].append(cur_known)


        if self.debug:
            self.render()
        
        self.frame_count += 1
        finished_bots = 0
        for bot in self.bots:
            if bot.disabled or bot.area_completed:
                finished_bots += 1
            
        if finished_bots == len(self.bots):
            self.data['success'] = False
            return True
        if cur_known == self.mutual_data['map'].size:
            self.data['success'] = True
            return True

        logging_end_time = psutil.Process().cpu_times().user
        self.data['logging_time'].append(logging_end_time - logging_time_start)


    def make_gif(self, frame_folder):
        print("Making gif")
        frame_folder = self.folder_name + "/gif"
        import glob
        from PIL import Image

        # get all image files in the folder in order
        frames = []
        imgs = glob.glob(frame_folder + "/*.png")
        # sort the image name scring numerically
        imgs.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
        for im in imgs:
            new_frame = Image.open(im)
            frames.append(new_frame)


        frame_one = frames[0]
        save_path = frame_folder + "/my_awesome.gif"
        frame_one.save(save_path, format="GIF", append_images=frames,
                save_all=True, duration=100, loop=0)

    def run_experiment(self, func_arr, *args , **kwargs):
        try:
            self.setup_run_now()
            done = False
            max_iter = self.cfg.ROWS**2 
            p_bar = tqdm.tqdm(total=max_iter, desc=f"{self.experiment_ID} {self.experiment_name}")
            for i in range(max_iter):
                if func_arr:
                    for func, func_args in zip(func_arr, args):
                        # append self to the args
                        func_args = list(func_args)
                        func_args.append(self)
                        func( *func_args, **kwargs) 

                # Save the Figure
                if self.cfg.CREATE_GIF:
                    assert self.cfg.LOG_PLOTS, "Must log plots to create gif"
                    # check if the folder exists
                    if not os.path.exists(self.folder_name + '/gif'):
                        os.makedirs(self.folder_name + '/gif')
                    self.log_plot_obj.map_fig.savefig(self.folder_name +f'/gif/{self.frame_count}.png', dpi=100)

                done = self.env_step()
                p_bar.update(1)
                if done:
                    # convert p_bar bar color to green
                    p_bar.set_description(f"✅ \033[92m {self.experiment_ID} {self.experiment_name} \033[0m")
                    p_bar.colour = 'green'
                    p_bar.close()
                    break
            else:
                # convert p_bar to red
                p_bar.colour = 'red'
                p_bar.close()
                # in red
                print("\033[91m" + "😱Max Iterations Reached:" + str(i) + "\033[0m")
                print("Experiment Failed:", self.experiment_name)
                self.data['success'] = False
                # remove the last logging time 
                self.data['logging_time'].pop()
                
            
            return self.clean_up_experiment()
        except Exception:
            # Orange the error
            print(f'\033[93m Error {traceback.format_exc()} \033[0m')
            # print(sys.exc_info()[2])
            print(f"\033[91m 🛑Error {self.experiment_ID} {self.experiment_name} \033[0m")


        