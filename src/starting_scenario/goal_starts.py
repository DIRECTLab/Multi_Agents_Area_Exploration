import numpy as np



class Rand_Start_Goal:
    def choose_start_gaol(self):
        self.goal_xy = self.get_random_point()

class Center_Start_Goal:
    def choose_start_goal(self):
        center_xy = (int(self.cfg.COLS//2), int(self.cfg.ROWS//2))
        self.goal_xy = center_xy

class Top_Left_Start_Goal:
    def choose_start_goal(self):
        top_left_xy = (1, 1)
        self.goal_xy = top_left_xy