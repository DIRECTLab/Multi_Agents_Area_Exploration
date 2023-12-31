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
from src.starting_scenario.starting_methods import *
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
        if cur_point[0] < 0 or cur_point[0] >= cfg.MAP_NP_ROWS//2 or \
            cur_point[1] < 0 or cur_point[1] >= cfg.MAP_NP_ROWS//2:
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
            x_arr, y_arr = np.mgrid[0:cfg.MAP_NP_ROWS, 0:cfg.MAP_NP_ROWS]
            cell = (self.pos_row, self.pos_column)
            dists = np.sqrt((x_arr - cell[0])**2 + (y_arr - cell[1])**2)
            return dists
    for row in range(cfg.MAP_NP_ROWS):
        grid.append([])
        for column in range(cfg.MAP_NP_ROWS):
            grid[row].append(Cell(row, column))
    return grid, matrix_list, agent_locs

#  related to our first voronoi calculation method
def generate_voronoi_division_grid(grid, bots, matrix_list, agent_locs, log_plot_obj=None):
    for i in range(len(bots)):
        column = bots[i].goal_xy[0]
        row = bots[i].goal_xy[1]
        grid[row][column].agent = True
        grid[row][column].agent_id = i
        grid[row][column].distance_matrix = grid[row][column].calc_distance_matrices()
        matrix_list.append(grid[row][column].distance_matrix)
        agent_locs.add((row, column))
        if log_plot_obj:
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
                start_method,
                goal_method,
                debug=False,
                figs=[]):
        self.cfg = cfg
        self.experiment_name = experiment_name
        self.Agent_Class_list = Agent_Class_list
        self.search_method = search_method
        self.return_dict = return_dict
        self.debug = debug
        self.experiment_ID = process_ID

        if cfg.DRAW_PYGAME_SIM:
            # Initialize pygame
            # check if  pygame is already initialized
            if not pygame.get_init():
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
            'total_distance_travelled' : [],
            }
        
        if 'Epsilon' in search_method:
            for i, agent in enumerate(self.Agent_Class_list):
                if 'Epsilon' in agent.__name__:
                    self.data[f'epsilon_{i}'] = []
            

        self.log_plot_obj = None
        if cfg.GRAPH_LOG_PLOTS:
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

        if cfg.DRAW_PYGAME_SIM:
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
        
        # OTHER_AGENT_LOCATIONS_GOAL.clear()
        # OTHER_AGENT_LOCATIONS_START.clear()
        start_locations = []
        goal_locations = []
        # place the goal locations
        if start_method == None:
            # throw an error if the start method is not defined
            assert False, "The start method is not defined"
        else:
            random.seed(cfg.SEED)
            np.random.seed(cfg.SEED)
            start_locations = start_method(cfg, self.ground_truth_map)

        if goal_method == None:
            # throw an error if the goal method is not defined
            assert False, "The goal method is not defined"
        else:
            random.seed(cfg.SEED)
            np.random.seed(cfg.SEED)
            goal_locations = goal_method(cfg, self.ground_truth_map)
        
        # Agent_Class_list
        for i, agent_class in enumerate(Agent_Class_list):
            self.bots.append(agent_class(
                        cfg = cfg,
                        id = i,
                        body_size = 20,
                        
                        lidar_range = self.ground_truth_map.shape[0]//4,
                        full_map = self.ground_truth_map,
                        position = start_locations[i],
                        goal_xy = goal_locations[i],
                        ax = bot_ax[i] if cfg.DRAW_PYGAME_SIM else None,
                        screen = self.cur_world.screen if cfg.DRAW_PYGAME_SIM else None,
                        lock= self.lock,
                    )
                )
            self.ground_truth_map[self.bots[-1].grid_position_xy[1]][self.bots[-1].grid_position_xy[0]] = cfg.AGENT_OBSTACLE
        
            if cfg.DRAW_PYGAME_SIM:
                bot_ax[i].set_title(f"Bot {i}")
                bot_ax[i].matshow(self.bots[i].agent_map)

        if 'Voronoi' in search_method:
            new_bot_list = []
            for bot in self.bots:
                if 'Voronoi' in bot.__class__.__name__:
                    new_bot_list.append(bot)

            self.minimum_comparison_table = generate_voronoi_division_grid(grid, new_bot_list, matrix_list, agent_locs, self.log_plot_obj)
            if cfg.GRAPH_LOG_PLOTS:
                self.log_plot_obj.map_ax.matshow(self.minimum_comparison_table, alpha=0.6)
            # assign each robot one voronoi region using assigned_points
            for bot_id in range(len(new_bot_list)):
                assigned_points = np.argwhere(self.minimum_comparison_table == bot_id)
                # convert list of list into list of tuples
                assigned_points = [tuple(point) for point in assigned_points]
                new_bot_list[bot_id].assigned_points = assigned_points
                assert len(assigned_points) > 0, "No points assigned to bot"
           
        self.frame_count = 0
        self.mutual_data = {}
        self.mutual_data['map'] = - np.ones((self.ground_truth_map.shape[0], self.ground_truth_map.shape[1])).astype(int)
        self.folder_name =  'data/' + experiment_name+ '/' + time.strftime("%Y-%m-%d_%H-%M-%S")
        if cfg.GRAPH_LOG_PLOTS:
            os.makedirs(self.folder_name)

            # self.log_plot_obj.plot_map(mutual_data, bots, data)
            self.log_plot_obj.map_ax.set_title(f"Max Known Area {self.ground_truth_map.size} \n {search_method}")
            # ensure the Title is not cut off
            # self.log_plot_obj.map_fig.tight_layout()
            if 'Voronoi' in search_method:
                self.log_plot_obj.map_ax.matshow(self.minimum_comparison_table, alpha=0.3)
            self.log_plot_obj.map_fig.savefig(self.folder_name + '/starting_map.png')

        # if cfg.DRAW_PYGAME_SIM:
        #     bot_fig.savefig(self.folder_name + '/starting_bot.png')
    
    # return [data, bots, ground_truth_map, mutual_data, self.log_plot_obj, self.minimum_comparison_table, cur_world, map_screen, self.folder_name, upscaling_down_sampled_map_for_vis]
    
    def setup_run_now(self):
        if self.cfg.DRAW_PYGAME_SIM:
            # Display the floor plan on the screen
            pygame.display.update()
            FPS = 600
            clock = pygame.time.Clock()

        # Wait for the user to close the window
        self.frame_count = 0
        self.sim_start_time = psutil.Process().cpu_times().user


    def clean_up_experiment(self):
            
        
        # create expeament folder
        os.makedirs(f"{self.folder_name}", exist_ok=True)

        if self.cfg.GRAPH_LOG_PLOTS:
            # update the ground_truth_map and plt
            self.log_plot_obj.plot_map(self.mutual_data['map'], self.bots, self.data)
            self.log_plot_obj.map_ax.set_title(f"Max Known Area {self.ground_truth_map.size}")
            if 'Voronoi' in self.search_method:
                self.log_plot_obj.map_ax.matshow(self.minimum_comparison_table, alpha=0.3)

            self.log_plot_obj.map_fig.savefig(f"{self.folder_name}/map_fig.png")

        # if self.cfg.DRAW_PYGAME_SIM:
        #     # save the screen
        #     pygame.image.save(self.cur_world.screen, f"{self.folder_name}/screen.png")
        #     pygame.quit()

        # save the config in jason format
        with open(f"{self.folder_name}/config.json", 'w') as f:
            json.dump(self.cfg.__dict__, f, indent=4)


        # save the data
        df = pd.DataFrame(self.data)
        # add the config to the data frame
        df['SEED'.lower()] = self.cfg.SEED 
        df['DRAW_PYGAME_SIM'.lower()] = self.cfg.DRAW_PYGAME_SIM
        df['GRAPH_LOG_PLOTS'.lower()] = self.cfg.GRAPH_LOG_PLOTS
        df['USE_THREADS'.lower()] = self.cfg.USE_THREADS
        df['N_BOTS'.lower()] = self.cfg.N_BOTS
        df['PYG_GRID_CELL_THICKNESS'.lower()] = self.cfg.PYG_GRID_CELL_THICKNESS
        # df['COLS'.lower()] = self.cfg.COLS
        # df['MAP_NP_ROWS'.lower()] = self.cfg.MAP_NP_ROWS
        df['ROOM_AREA'.lower()] = self.cfg.PYG_SCREEN_WIDTH * self.cfg.PYG_SCREEN_HEIGHT
        df['PYG_MIN_ROOM_SIZE'.lower()] = self.cfg.PYG_MIN_ROOM_SIZE / self.cfg.PYG_GRID_CELL_THICKNESS
        # df['MAX_ROOM_SIZE'.lower()] = self.cfg.MAX_ROOM_SIZE / self.cfg.PYG_GRID_CELL_THICKNESS
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
        if self.cfg.DRAW_PYGAME_SIM:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            # self.clock.tick(self.FPS)
            # update the scrren
            pygame.display.update()
            self.cur_world.screen.blit(self.map_screen, (0, 0))
            # print("clock.get_fps()",self.clock.get_fps(), end='\r')

        if self.cfg.GRAPH_LOG_PLOTS:
            # update the ground_truth_map and plt
            self.log_plot_obj.plot_map(self.mutual_data['map'], self.bots, self.data)

            tittle = (self.experiment_name).replace("/", "\n").replace('_',' ').title() + f"\nMax Known Area {self.ground_truth_map.size}"
            self.log_plot_obj.map_ax.set_title(tittle)
            if 'Voronoi' in self.search_method :
                self.log_plot_obj.map_ax.matshow(self.minimum_comparison_table, alpha=0.3)


        if self.cfg.DRAW_PYGAME_SIM or self.cfg.GRAPH_LOG_PLOTS:
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
            t = pool.apply_async(bot.update, (self.mutual_data,self.cfg.DRAW_PYGAME_SIM ))
            threads.append(t)
        for i, (t, bot)  in enumerate(zip(threads,self.bots)):
            [length, dist] = t.get()
            path_length += length


    def env_step(self):
        # This is the main loop of the simulation
        path_length = 0
        replan_count = 0
        total_distance = 0
        if self.cfg.USE_THREADS:
            self.spawn_update_thread()
            end_time = psutil.Process().cpu_times().user
        else:
            # time the bot update
            start_time = psutil.Process().cpu_times().user
            for i, bot in enumerate(self.bots):
                bot.update(self.mutual_data, draw=self.cfg.DRAW_PYGAME_SIM)
                bot.frame_count =self.frame_count
                path_length += len(bot.plan if bot.plan is not None else [])
                replan_count += bot.replan_count
                total_distance += bot.total_dist_traveled
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
        self.data['total_distance_travelled'].append(total_distance)


        if self.debug:
            self.render()
        
        self.frame_count += 1
        finished_bots = 0
        disabled_bots = 0
        for bot in self.bots:
            if bot.area_completed:
                finished_bots += 1
            elif bot.disabled:
                disabled_bots += 1
        # print('finished_bots', finished_bots)
        # print('disabled_bots', disabled_bots)
        
        if finished_bots == len(self.bots):
            self.data['success'] = True
            return True
        if cur_known == self.mutual_data['map'].size:
            self.data['success'] = True
            return True
        if finished_bots + disabled_bots == len(self.bots):
            self.data['success'] = False
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
            # max_iter = self.cfg.GRID_SIZE**2
            max_iter = self.mutual_data['map'].size
            p_bar = tqdm.tqdm(total=max_iter, desc=f"{self.experiment_ID} {self.experiment_name}")
            for i in range(max_iter):
                if func_arr:
                    for func, func_args in zip(func_arr, args):
                        # append self to the args
                        func_args = list(func_args)
                        func_args.append(self)
                        func( *func_args, **kwargs)
                
                if len(self.data["area_percent"]) ==0:
                    area_progress ='0.0'
                else:
                    area_progress = f'{self.data["area_percent"][-1]*100:.2f}'

                # Save the Figure
                if self.cfg.CREATE_GIF:
                    assert self.cfg.GRAPH_LOG_PLOTS, "Must log plots to create gif"
                    # check if the folder exists
                    if not os.path.exists(self.folder_name + '/gif'):
                        os.makedirs(self.folder_name + '/gif')
                    self.log_plot_obj.map_fig.savefig(self.folder_name +f'/gif/{self.frame_count}.png', dpi=100)

                if i%10 == 0:
                    p_bar.update(10)
                    p_bar.set_description(f"{self.experiment_ID} {self.experiment_name}: area {area_progress}% ")
                    
                done = self.env_step()
                if done:
                    # convert p_bar bar color to green
                    p_bar.set_description(f"✅ \033[92m {self.experiment_ID} {self.experiment_name}: area {area_progress}% \033[0m")
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


        