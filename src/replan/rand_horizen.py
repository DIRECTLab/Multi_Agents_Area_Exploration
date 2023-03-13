import numpy as np

class Rand_Frontier:
    # def __init__(self, cfg, agent_map, agent_pos, ground_truth_map):
    #     self.cfg = cfg
    #     self.agent_map = agent_map
    #     self.agent_pos = agent_pos
    #     self.ground_truth_map = ground_truth_map
    def get_random_point(self):
        # make sure the goal is not in the obstacle
        while True:
            point_rc = (np.random.randint(self.ground_truth_map.shape[0]), np.random.randint(self.ground_truth_map.shape[1]))
            if self.ground_truth_map[point_rc] == self.cfg.EMPTY:
                point_xy = (point_rc[1], point_rc[0])
                break
        return point_xy
        
    def get_random_unnknown(self):
        unknown_points = np.argwhere(self.agent_map == self.cfg.UNKNOWN)
        if len(unknown_points) == 0:
            # return self.get_random_point()
            print("get_random_unnknown(): No unknown points")
            # set goal as current position
            self.plan = []
            self.area_completed = True
            return [-1,-1]
        elif len(unknown_points) == 1:
            return (unknown_points[0][1], unknown_points[0][0])
        # choose a random UNKNOWN
        idx = np.random.randint(len(unknown_points))
        return (unknown_points[idx][1], unknown_points[idx][0])

    def get_random_frontier(self):
        frontier_points = np.argwhere(self.agent_map == self.cfg.FRONTIER)
        if len(frontier_points) == 0:
            return self.get_random_unnknown()
        elif len(frontier_points) == 1:
            return (frontier_points[0][1], frontier_points[0][0])
        # choose a random frontier
        idx = np.random.randint(len(frontier_points))
        return (frontier_points[idx][1], frontier_points[idx][0])
    
    def get_goal_method(self):
        return self.get_random_frontier()

    # def set_new_goal(self):
    #     # self.goal = self.get_random_point()
    #     self.goal = self.get_random_frontier()
    #     # if self.goal == self.grid_position:
    #     assert self.goal != self.grid_position, "Goal and position are the same"