import pygame
import numpy as np
class Config:
    def __init__(self, scenario, parameters, debug):
        [Method, run_type, start, goal,
                map_length,agent_count, experiment_iteration, min_rom_size] = scenario
        if debug:
            self.DRAW_PYGAME_SIM = True
            self.GRAPH_LOG_PLOTS = True
        else:
            self.DRAW_PYGAME_SIM = False
            self.GRAPH_LOG_PLOTS = False

        self.USE_THREADS = False
        self.CREATE_GIF = parameters.Create_gif
        self.USE_PROCESS = parameters.Use_process
        
        self.SEED = int(map_length + experiment_iteration)
        self.N_BOTS = int(agent_count)
        
        # Define the size of the screen
        self.MAP_NP_COLS = map_length
        self.MAP_NP_ROWS = map_length

        # The Ground truth map is a 2D array of booleans
        self.AGENT_OBSTACLE = 3.0
        self.MINE = 2.0
        self.EMPTY = 1.0
        self.OBSTACLE = 0.0

        # Map location definitions for agent_map
        self.UNKNOWN = -1
        self.KNOWN_WALL = 0
        self.KNOWN_EMPTY = 1
        self.FRONTIER = 2

        # Types of robot loss
        self.ROBOT_LOSS_TYPE = run_type.__name__
        # self.MINE_DENSITY = .1
        # this is a change to match the //1000 that use to be in the code
        # num_mines = self.cfg.MINE_DENSITY * self.cfg.MAP_NP_ROWS * self.cfg.MAP_NP_COLS
        # self.MINE_DENSITY = 0.0676 
        self.MINE_DENSITY = 0.01

        ## PYGAME CONFIGs 🐍
        # Define the size of the walls, this is only for looks/ZOOM
        # get monitor size
        if self.DRAW_PYGAME_SIM:
            pygame.init()

            monitor_size = (int(pygame.display.Info().current_w), int(pygame.display.Info().current_h))
            monitor_size = np.min(monitor_size)
            # scale the grid cell thickness to the monitor size
            # ❗️unsable for now
            # self.PYG_GRID_CELL_THICKNESS = int(monitor_size / self.MAP_NP_COLS)
        else:
            # ❗️unsable for now
            # self.PYG_GRID_CELL_THICKNESS = 1
            pass
        self.PYG_GRID_CELL_THICKNESS = 10

        self.PYG_SCREEN_WIDTH = self.MAP_NP_COLS * self.PYG_GRID_CELL_THICKNESS
        self.PYG_SCREEN_HEIGHT = self.MAP_NP_ROWS * self.PYG_GRID_CELL_THICKNESS
        
        # Define the minimum and maximum sizes for the rooms
        self.PYG_MIN_ROOM_SIZE = min_rom_size * self.PYG_GRID_CELL_THICKNESS

        # Define the colors to be used in the drawing
        self.BACKGROUND_COLOR = (78, 157, 157)
        self.WALL_COLOR = (80, 24, 99)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (251, 233, 89)
        self.PINK = (255, 0, 255)
        self.ORANGE = (255, 165, 0)
        self.PURPLE = (128, 0, 128)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.TEAL = (0, 128, 128)