import numpy as np
from src.agent import Agent

class Voronoi_Random_Frontier_Help_Others(Agent):
    def get_random_unnknown(self):
        unknown_points = np.argwhere(self.agent_map == self.cfg.UNKNOWN)
        if len(unknown_points) == 0:
            self.plan = []
            self.area_completed = True
            print(f"The bot {self.id} finished ALL exploration his own region... Now will help others...")
            return self.grid_position_xy
        unknown_points_assigned = []
        for point in unknown_points:
            if tuple(point) in self.assigned_points:
                unknown_points_assigned.append(point)
        if len(unknown_points_assigned) == 0:
            # self.plan = []
            # self.area_completed = True
            print(f"The bot {self.id} finished exploration his own region... Now will help others...")
            # return self.grid_position_xy
            idx = np.random.randint(len(unknown_points))
            cor_tuple = tuple(unknown_points[idx])
            print(cor_tuple[1], cor_tuple[0])
            return (cor_tuple[1], cor_tuple[0])
        elif len(unknown_points_assigned) == 1:
            print(unknown_points_assigned[0][1], unknown_points_assigned[0][0])
            return (unknown_points_assigned[0][1], unknown_points_assigned[0][0])
        # choose a random UNKNOWN
        idx = np.random.randint(len(unknown_points_assigned))
        print(idx)
        print(unknown_points_assigned[idx][1], unknown_points_assigned[idx][0])

        return (unknown_points_assigned[idx][1], unknown_points_assigned[idx][0])
    
    def get_random_frontier(self):
        frontier_points = np.argwhere(self.agent_map == self.cfg.FRONTIER)
        frontier_points_assigned = []
        for point in frontier_points:
            if tuple(point) in self.assigned_points:
                frontier_points_assigned.append(point)
        if len(frontier_points_assigned) == 0:
            return self.get_random_unnknown()
        elif len(frontier_points_assigned) == 1:
            return (frontier_points_assigned[0][1], frontier_points_assigned[0][0])
        # choose a random frontier
        idx = np.random.randint(len(frontier_points_assigned))
        return (frontier_points_assigned[idx][1], frontier_points_assigned[idx][0])
    
    def get_goal_method(self):
        return self.get_random_frontier()
