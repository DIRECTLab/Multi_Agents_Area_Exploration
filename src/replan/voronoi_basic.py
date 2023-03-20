import numpy as np
from src.agent import Agent

class Voronoi_Frontier_Closest(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.random_frontier = False

    def my_area_done(self, done_search_points):
        return self.grid_position_xy

    def get_goal_method(self):

        # find the unknown 'OR' frontier points
        unknown_points = np.argwhere((self.agent_map == self.cfg.UNKNOWN) | ( self.agent_map == self.cfg.FRONTIER) )
        if len(unknown_points) == 0:
            # this is the case when all the points are known
            self.plan = []
            self.area_completed = True
            return self.grid_position_xy
        
        if self.area_completed:
            # now the agent can help others
            return self.my_area_done(unknown_points)
        
        assigned_assigned = []
        for point in unknown_points:
            if tuple(point) in self.assigned_points:
                assigned_assigned.append(point)

        # Get a random frontier point
        frontier_point = self.get_new_location_xy(assigned_assigned, self.cfg.FRONTIER, useRandom=self.random_frontier)
        if frontier_point:
            # Found a frontier point
            return frontier_point
        
        # Get a random unknown point
        unknown_point = self.get_new_location_xy(np.array(assigned_assigned), self.cfg.UNKNOWN, useRandom=self.random_frontier)
        if unknown_point is None:
            self.plan = []
            self.area_completed = True
            # run the end of assignment function
            return self.my_area_done(unknown_points)
        
        return unknown_point

class Voronoi_Frontier_Random(Voronoi_Frontier_Closest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.random_frontier = True

class Voronoi_Frontier_Help_Others(Voronoi_Frontier_Closest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def my_area_done(self, done_search_points):
        self.area_completed = False
        if len(done_search_points) == 0:
            return self.grid_position_xy
        idx = np.random.randint(len(done_search_points))
        point = tuple(done_search_points[idx])
        # return in X, Y format
        return (point[1], point[0])

