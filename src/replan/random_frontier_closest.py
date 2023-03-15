import numpy as np

class Random_Frontier_Closest:
    
    def get_closet_unknown(self):
        unknown_points = np.argwhere(self.agent_map == self.cfg.UNKNOWN)
        if len(unknown_points) == 0:
            # return self.get_closet_unknown()
            #print("get_closet_unknown(): No unknown points")
            # set goal as current position
            self.plan = []
            self.area_completed = True
            return [-1,-1]
        elif len(unknown_points) == 1:
            return (unknown_points[0][1], unknown_points[0][0])
        # choose a random UNKNOWN
        idx = self.get_closest_point_rc(list(unknown_points))
        return (idx[1], idx[0])

    def get_closet_frontier(self):
        frontier_points = np.argwhere(self.agent_map == self.cfg.FRONTIER)
        if len(frontier_points) == 0:
            return self.get_closet_unknown()
        elif len(frontier_points) == 1:
            return (frontier_points[0][1], frontier_points[0][0])
        # choose a random frontier
        idx = self.get_closest_point_rc(list(frontier_points))
        return (idx[1], idx[0])
    
    def get_goal_method(self):
        return self.get_closet_frontier()
