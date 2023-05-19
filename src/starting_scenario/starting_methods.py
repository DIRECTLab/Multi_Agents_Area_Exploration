import numpy as np
import math
from itertools import product, starmap, islice
from src.starting_scenario.base_start import Base_Start

#  will make sure we have different random points over grid for agent positions
OTHER_AGENT_LOCATIONS_POSITION = []

class Manual_Start:
    four_start_pos = [(2, 7), (9, 16), (2, 5), (3, 11)]
    def choose_start_position(self):
        self.grid_position_xy = self.four_start_pos[self.id]

class Rand_Start_Position(Base_Start):
    def choose_start_position(self):
        self.grid_position_xy = self.get_random_point()
        if self.grid_position_xy not in OTHER_AGENT_LOCATIONS_POSITION:
            OTHER_AGENT_LOCATIONS_POSITION.append(self.grid_position_xy)
        else:
            self.grid_position_xy = self.get_random_point()
            OTHER_AGENT_LOCATIONS_POSITION.append(self.grid_position_xy)

class Center_Start_Position(Base_Start):
    def choose_start_position(self):
        self.grid_position_xy = self.points_over_radious(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS, 'center')[self.id]
        self.grid_position_xy = (int(np.round(self.grid_position_xy[0])), int(np.round(self.grid_position_xy[1])))

        (found_goal,self.grid_position_xy)  = self.check_if_valid_point(self.grid_position_xy ,self.ground_truth_map, self.cfg, OTHER_AGENT_LOCATIONS_POSITION)
        if not found_goal:
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.grid_position_xy)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.grid_position_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.grid_position_xy)
            return

class Top_Left_Start_Position(Base_Start):
    def choose_start_position(self):
        self.grid_position_xy = self.points_over_radious(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS, 'topleft')[self.id]
        self.grid_position_xy = (int(np.round(self.grid_position_xy[0])), int(np.round(self.grid_position_xy[1])))
        
        (found_goal,self.grid_position_xy)  = self.check_if_valid_point(self.grid_position_xy ,self.ground_truth_map, self.cfg, OTHER_AGENT_LOCATIONS_POSITION)
        if not found_goal:
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.grid_position_xy)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.grid_position_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.grid_position_xy)
            return

class Edge_Start_Position(Base_Start):
    def choose_start_position(self):
        self.grid_position_xy = self.points_on_rectangle_edge(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS)[self.id]
        self.grid_position_xy = (int(np.round(self.grid_position_xy[0])), int(np.round(self.grid_position_xy[1])))
        (found_goal,self.grid_position_xy)  = self.check_if_valid_point(self.grid_position_xy ,self.ground_truth_map, self.cfg, OTHER_AGENT_LOCATIONS_POSITION)
        if not found_goal:
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.grid_position_xy)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.grid_position_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.grid_position_xy)
            return

class Distributed_Start(Base_Start):
    def choose_start_position(self):
        self.grid_position_xy = self.dividegrid(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS)[self.id]
        self.grid_position_xy = (int(np.round(self.grid_position_xy[0])), int(np.round(self.grid_position_xy[1])))

        (found_goal,self.grid_position_xy)  = self.check_if_valid_point(self.grid_position_xy ,self.ground_truth_map, self.cfg, OTHER_AGENT_LOCATIONS_POSITION)
        if not found_goal:
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.grid_position_xy,)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.grid_position_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.grid_position_xy)
            return
            
