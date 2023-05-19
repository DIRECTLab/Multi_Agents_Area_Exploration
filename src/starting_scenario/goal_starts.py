import numpy as np
import math
from itertools import product, starmap, islice
from src.starting_scenario.base_start import Base_Start

OTHER_AGENT_LOCATIONS_GOAL=[]

class Manual_Goal:
    four_goal_pos = [(10,10), (20,20), (30,30), (45,45)]
    def choose_start_goal(self):
        self.goal_xy = self.four_goal_pos[self.id]

class Rand_Start_Goal(Base_Start):
    def choose_start_goal(self):
        self.goal_xy = self.get_random_point()
        if self.goal_xy not in OTHER_AGENT_LOCATIONS_GOAL:
            OTHER_AGENT_LOCATIONS_GOAL.append(self.goal_xy)
        else:
            self.goal_xy = self.get_random_point()
            OTHER_AGENT_LOCATIONS_GOAL.append(self.goal_xy)

class Center_Start_Goal(Base_Start):
    def choose_start_goal(self):

        self.goal_xy = self.points_over_radious(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS, 'center')[self.id]
        self.goal_xy = (int(np.round(self.goal_xy[0])), int(np.round(self.goal_xy[1])))

        (found_goal, self.goal_xy) = self.check_if_valid_point(self.grid_position_xy ,self.ground_truth_map, self.cfg, OTHER_AGENT_LOCATIONS_GOAL)
        if not found_goal:
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.goal_xy)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.goal_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.goal_xy)
            return
        
class Top_Left_Start_Goal(Base_Start):
    def choose_start_goal(self):

        self.goal_xy = self.points_over_radious(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS, 'topleft')[self.id]
        self.goal_xy = (int(np.round(self.goal_xy[0])), int(np.round(self.goal_xy[1])))
        
        (found_goal, self.goal_xy) =  self.check_if_valid_point(self.grid_position_xy ,self.ground_truth_map, self.cfg, OTHER_AGENT_LOCATIONS_GOAL)
        if not found_goal:
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.goal_xy)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.goal_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.goal_xy)
            return

class Edge_Start_Goal(Base_Start):
    def choose_start_goal(self):
        
        self.goal_xy = self.points_on_rectangle_edge(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS)[self.id]
        self.goal_xy = (int(np.round(self.goal_xy[0])), int(np.round(self.goal_xy[1])))        
        
        (found_goal, self.goal_xy) =  self.check_if_valid_point(self.grid_position_xy ,self.ground_truth_map, self.cfg, OTHER_AGENT_LOCATIONS_GOAL)
        if not found_goal:
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.goal_xy)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.goal_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.goal_xy)
            return

class Distributed_Goal(Base_Start):
    def choose_start_goal(self):
        self.goal_xy = self.dividegrid(self.cfg.ROWS, self.cfg.COLS, self.cfg.N_BOTS)[self.id]
        self.goal_xy = (int(np.round(self.goal_xy[0])), int(np.round(self.goal_xy[1])))
        
        (found_goal, self.goal_xy) =  self.check_if_valid_point(self.grid_position_xy ,self.ground_truth_map, self.cfg, OTHER_AGENT_LOCATIONS_GOAL)
        if not found_goal:
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", self.goal_xy,)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(self.ground_truth_map == self.cfg.EMPTY)
            self.goal_xy = self.get_closest_point_rc(empty_points_rc)
            print("new closest point to the edge: ", self.goal_xy)
            return




