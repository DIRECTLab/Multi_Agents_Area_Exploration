import numpy as np

class Voronoi_Random_Closest_Frontier():
    def get_closet_unknown(self):
        # finds the classes unknown point
        unknown_points = np.argwhere(self.agent_map == self.cfg.UNKNOWN)
        unknown_points_assigned = []
        for point in unknown_points:
            if tuple(point) in self.assigned_points:
                unknown_points_assigned.append(point)
        if len(unknown_points_assigned) == 0:
            # return self.get_random_point()
            #print("get_closet_unknown(): No unknown points")
            # set goal as current position
            self.plan = []
            self.area_completed = True
            return self.grid_position_xy
        elif len(unknown_points_assigned) == 1:
            return (unknown_points_assigned[0][1], unknown_points_assigned[0][0])
        # choose the closest UNKNOWN
        nest_point = self.get_closest_point_rc(unknown_points_assigned)
        return (nest_point[1], nest_point[0])

    def get_closet_frontier(self):
        frontier_points = np.argwhere(self.agent_map == self.cfg.FRONTIER)
        frontier_points_assigned = []
        for point in frontier_points:
            if tuple(point) in self.assigned_points:
                frontier_points_assigned.append(point)
        if len(frontier_points_assigned) == 0:
            return self.get_closet_unknown()
        elif len(frontier_points_assigned) == 1:
            return (frontier_points_assigned[0][1], frontier_points_assigned[0][0])
        # choose the closest frontier
        nest_point = self.get_closest_point_rc(frontier_points_assigned)
        return (nest_point[1], nest_point[0])

    def get_goal_method(self):
        return self.get_closet_frontier()
