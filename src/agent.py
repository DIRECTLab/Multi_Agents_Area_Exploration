# this hold the agent class

import math
import pygame
import numpy as np
import matplotlib.pyplot as plt
import warnings
from src.planners.astar_new import astar
from src.point_utils.point_find import *

def bresenham(start, end):
    """
    Implementation of Bresenham's line drawing algorithm
    See en.wikipedia.org/wiki/Bresenham's_line_algorithm
    Bresenham's Line Algorithm
    Produces a np.array from start and end (original from roguebasin.com)
    >>> points1 = bresenham((4, 4), (6, 10))
    >>> print(points1)
    np.array([[4,4], [4,5], [5,6], [5,7], [5,8], [6,9], [6,10]])
    """
    # setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    is_steep = abs(dy) > abs(dx)  # determine how steep the line is
    if is_steep:  # rotate line
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    # swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True
    dx = x2 - x1  # recalculate differentials
    dy = y2 - y1  # recalculate differentials
    error = int(dx / 2.0)  # calculate error
    y_step = 1 if y1 < y2 else -1
    # iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = [y, x] if is_steep else (x, y)
        points.append(coord)
        # print(points)
        error -= abs(dy)
        if error < 0:
            y += y_step
            error += dx
    if swapped:  # reverse the list if the coordinates were swapped
        points.reverse()
    points = np.array(points)
    return points

class Agent():
    def __init__(self, 
                cfg,
                id, 
                body_size,
                grid_size,
                window_size,
                lidar_range, 
                full_map,
                assigned_points =None,
                position=None,
                goal_xy=None,
                color=(0,255,0),
                ax=None,
                screen=None,
                lock = None):
        self.cfg = cfg
        self.id = id
        self.body_size = body_size
        self.grid_size = grid_size
        self.window_size = window_size
        self.ground_truth_map = full_map.copy()
        self.agent_map = np.zeros((full_map.shape[0], full_map.shape[1])).astype(int)
        self.agent_map.fill(self.cfg.UNKNOWN)
        self.assigned_points = assigned_points
        self.area_completed = False

        self.cur_color = color
        self.lidarRange = lidar_range
        self.lidar_sweep_res = (np.arctan2(1, self.lidarRange)%np.pi ) * 2
        self.lidar_step_res = 1
        self.replan_count = 0

        self.goal_xy = None
        self.grid_position_xy = None
        self.grid_position_xy = position
        self.goal_xy = goal_xy
        assert self.grid_position_xy is not None, "grid_position_xy is None, the Base method is not implemented"
        assert self.goal_xy is not None, "goal_xy is None, the Base method is not implemented"
        self.plan = None

        self.ax = ax
        self.screen = screen

        self.lock = lock
        # Start at 0 velocity
        self.dx= 0
        self.dy= 0
        self.total_dist_traveled = 0
        self.past_traversed_locations =[self.grid_position_xy]
        self.frame_count = 0
        self.choose_random = None

        self.disabled = False

        self.scan()
        self.replan({})
    
    def set_new_goal(self):
        self.goal_xy = self.get_goal_method()
        assert self.goal_xy is not None, "goal_xy is None, the Base method is not implemented"

    def replan(self, mutual_data):
        self.replan_count += 1

        if self.area_completed:
            return
        # # check id the goal_xy is known
        self.plan = astar(  np.where(self.agent_map == self.cfg.KNOWN_WALL, self.cfg.KNOWN_WALL, self.cfg.KNOWN_EMPTY), 
                            (int(np.round(self.grid_position_xy[0])), int(np.round(self.grid_position_xy[1]))),
                            self.goal_xy)
        if self.plan == None:
            if self.replan_count > 100:
                warnings.warn("Replan count is too high")
            assert self.replan_count < self.agent_map.size, f"Replan count is too high {self.agent_map.size}"

            self.set_new_goal()
            self.replan(mutual_data)
            return

        # remove the current position
        # if len(self.plan) > 0:
        #     self.plan.pop(0)
        #     print("following element is popped", self.plan.pop(0), "for agent", self.id)

    def arrow( self, lcolor, tricolor, start, end, trirad, thickness=2):
        rad = math.pi/180
        pygame.draw.line(self.screen, lcolor, start, end, thickness)
        rotation = (math.atan2(start[1] - end[1], end[0] - start[0])) + math.pi/2

        # right triangle
        pygame.draw.polygon(self.screen, tricolor, 
            ((end[0] + trirad * math.sin(rotation), end[1] + trirad * math.cos(rotation)),
            (end[0] + trirad * math.sin(rotation - 90*rad),end[1] + trirad * math.cos(rotation - 90*rad)),
            (end[0] + trirad * math.sin(rotation + 90*rad),end[1] + trirad * math.cos(rotation + 90*rad))))

    # @profile
    def draw(self):    
        somthing_drawn = False
        # draw an arrow in the direction of dx, dy
        if self.screen is not None:
            somthing_drawn = True
            self.arrow(self.cfg.BLUE, 
                        self.cfg.YELLOW, 
                        (self.grid_position_xy[0]* self.grid_size,self.grid_position_xy[1]* self.grid_size),
                        (self.grid_position_xy[0]* self.grid_size + self.dx * self.grid_size,
                        self.grid_position_xy[1]* self.grid_size + self.dy * self.grid_size),
                        10)

        # update plt plot
        # clear the plot
        if self.ax is not None:
            somthing_drawn = True
            self.ax.clear()
            self.ax.matshow(self.agent_map)
            self.ax.plot(self.grid_position_xy[0], self.grid_position_xy[1], markersize=1, marker='.', color=np.array(self.cur_color)/255)

        # draw the plan line in pygame
        if self.ax is not None or self.screen is not None:
            somthing_drawn = True
            for i in range(len(self.plan)-1):
                if self.screen is not None:
                    somthing_drawn = True
                    pygame.draw.line(self.screen, color= self.cfg.GREEN,
                                    start_pos=(self.plan[i][0]* self.grid_size,self.plan[i][1]* self.grid_size),
                                    end_pos=(self.plan[i+1][0]* self.grid_size,self.plan[i+1][1]* self.grid_size),
                                    width=self.grid_size//4)
                # draw plt line
                if self.ax is not None:
                    self.ax.plot([self.plan[i][0], self.plan[i+1][0]], [self.plan[i][1], self.plan[i+1][1]], color=np.array(self.cfg.GREEN)/255)
        if not somthing_drawn:
            warnings.warn("No drawing method is set, please set ax or screen")

    
    
    # Function to detect obstacles using Bresenham's line algorithm
    def detect_obstacles(self, start_x, start_y, end_x, end_y):
        dx = abs(end_x - start_x)
        dy = abs(end_y - start_y)
        sx = 1 if start_x < end_x else -1
        sy = 1 if start_y < end_y else -1

        x = start_x
        y = start_y

        obstacles = []

        if dx > dy:
            err = dx / 2.0
            while x != end_x:
                if x >= 0 and x < self.grid_size and y >= 0 and y < self.grid_size:  # Check valid range
                    if self.ground_truth_map[y][x] == self.cfg.OBSTACLE:
                        obstacles.append((x, y))

                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != end_y:
                if x >= 0 and x < self.grid_size and y >= 0 and y < self.grid_size:  # Check valid range
                    if self.ground_truth_map[y][x] == self.cfg.OBSTACLE:
                        obstacles.append((x, y))

                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        # print(obstacles)
        return obstacles
    

    def move(self, mutual_data):
        # Update the agent's position
        cur_x = self.grid_position_xy[0]
        cur_y = self.grid_position_xy[1]
        
        next_path_point = self.plan[0]
        if (int(np.round(cur_x)), int(np.round(cur_y))) == (next_path_point[0], next_path_point[1]):
            # get the next point
            self.plan.pop(0)
            next_path_point = self.plan[0]
        else:
            # # get the direction from current position to next point
            # #  scale such that the sum of the squares of the components is velocity
            # velocity = 1
            # # self.dx = velocity * (self.goal_xy[0] - cur_x) / np.sqrt((self.goal_xy[0] - cur_x)**2 + (self.goal_xy[1] - cur_y)**2)
            # # self.dy = velocity * (self.goal_xy[1] - cur_y) / np.sqrt((self.goal_xy[0] - cur_x)**2 + (self.goal_xy[1] - cur_y)**2)
            # # draw a line to the next point

            # # move towards the next point
            # direction = (next_path_point[0] - cur_x, next_path_point[1] - cur_y)
            # self.dx = velocity * direction[0] / np.sqrt(direction[0]**2 + direction[1]**2)
            # self.dy = velocity * direction[1] / np.sqrt(direction[0]**2 + direction[1]**2)    self.grid_position = next_path_point
            pass



        self.total_dist_traveled += np.sqrt((next_path_point[0] - cur_x)**2 + (next_path_point[1] - cur_y)**2)
        self.grid_position_xy = next_path_point
        self.past_traversed_locations.append(self.grid_position_xy)
        return

        new_position = (self.grid_position_xy[0] + self.dx, self.grid_position_xy[1] + self.dy)
        new_x = new_position[0]
        new_y = new_position[1]

        # boundary collision
        if new_x < 0 or new_x >= self.agent_map.shape[0]:
            self.dx *= -1
            return 
        if new_y < 0 or new_y >= self.agent_map.shape[1]:
            self.dy *= -1
            return
        if new_x == np.NAN or new_y == np.NAN:
            # raise Exception("Agent collided with wall")
            print("Agent collided with wall")
            return
        # wall collision
        sampled_next_point = self.ground_truth_map[int(np.round(new_y)), int(np.round(new_x))]
        if sampled_next_point == False:# obstacle
            # move in the direction from sampeld_point to position
            self.dx *= -1
            self.dy *= -1
            # throw an error
            # raise Exception("Agent collided with obstacle")
        
        self.total_dist_traveled += np.sqrt((self.grid_position_xy[0] - new_position[0])**2 + (self.grid_position_xy[1] - new_position[1])**2)
        self.grid_position_xy = new_position

    def scan(self):
        # send out scan to update local built_map
        for angle in range(0, 360, 5):
            x, y = self.grid_position_xy[0] * 10 + 10 // 2, self.grid_position_xy[1] * 10 + 10 // 2
            end_x = int(x + self.lidarRange * 10 * math.cos(math.radians(angle)))
            end_y = int(y + self.lidarRange * 10 * math.sin(math.radians(angle)))

            obstacles = self.detect_obstacles(x//10, y//10, end_x//10, end_y//10)
            
            if obstacles:
                obstacle_x = obstacles[0][0]
                obstacle_y = obstacles[0][1]
                free_area = bresenham((x//10, y//10), (obstacle_x, obstacle_y))

                for fa in free_area:
                    # if OBSTACLE
                    if self.ground_truth_map[fa[1]][fa[0]] == self.cfg.OBSTACLE:
                        self.agent_map[fa[1]][fa[0]] = self.cfg.KNOWN_WALL
                        if self.screen is not None:
                            pygame.draw.line(self.screen, (255, 0, 0), (x, y), (obstacle_x * 10 + 10 // 2, obstacle_y * 10 + 10 // 2))
                        continue
                    # if EMPTY
                    if self.ground_truth_map[fa[1]][fa[0]] == self.cfg.EMPTY or self.ground_truth_map[fa[1]][fa[0]] == self.cfg.MINE:
                        self.agent_map[fa[1]][fa[0]] = self.cfg.KNOWN_EMPTY
                        if self.screen is not None:
                            pygame.draw.line(self.screen, (0, 255, 0), (x, y), (obstacle_x * 10 + 10 // 2, obstacle_y * 10 + 10 // 2))
                        continue

                    # # if Mine
                    # if self.ground_truth_map[fa[1]][fa[0]] == self.cfg.MINE:
                    #     self.agent_map[fa[1]][fa[0]] = self.cfg.MINE
                    #     if self.screen is not None:
                    #         pygame.draw.line(self.screen, (0, 0, 255), (x, y), (obstacle_x * 10 + 10 // 2, obstacle_y * 10 + 10 // 2))
                    #     continue
                continue
        
            if len(obstacles) == 0:
                free_area = bresenham((x//10, y//10), (end_x//10, end_y//10))

                for fa in free_area:
                    # if OBSTACLE
                    if self.ground_truth_map[fa[1]][fa[0]] == self.cfg.OBSTACLE:
                        self.agent_map[fa[1]][fa[0]] = self.cfg.KNOWN_WALL
                        if self.screen is not None:
                            pygame.draw.line(self.screen, (255, 0, 0), (x, y), (end_x, end_y))
                        continue

                    # if EMPTY
                    if self.ground_truth_map[fa[1]][fa[0]] == self.cfg.EMPTY or self.ground_truth_map[fa[1]][fa[0]] == self.cfg.MINE:
                        self.agent_map[fa[1]][fa[0]] = self.cfg.KNOWN_EMPTY
                        if self.screen is not None:
                            pygame.draw.line(self.screen, (0, 255, 0), (x, y), (end_x, end_y))
                        continue

                    # # if Mine
                    # if self.ground_truth_map[fa[1]][fa[0]] == self.cfg.MINE:
                    #     self.agent_map[fa[1]][fa[0]] = self.cfg.MINE
                    #     if self.screen is not None:
                    #         pygame.draw.line(self.screen, (0, 0, 255), (x, y), (end_x, end_y))
                    #     continue

                # if self.ground_truth_map[end_y//10, end_x//10] == self.cfg.MINE:
                #     self.agent_map[end_y//10, end_x//10] = self.cfg.MINE
                #     continue


                if self.ground_truth_map[end_y//10, end_x//10] != self.cfg.OBSTACLE:
                    self.agent_map[end_y//10, end_x//10] = self.cfg.FRONTIER
                    continue




    # def scan(self):
    #     # send out scan to update local built_map
    #     for i, angle in enumerate(np.arange(0, 2*np.pi, self.lidar_sweep_res)):

    #         x, y = self.grid_position_xy

    #         ray_cast_samples = np.arange(0,self.lidarRange, self.lidar_step_res)
    #         for j, r in enumerate(ray_cast_samples):
    #             # self.world_ax.add_patch(plt.Circle((self.pose_rc[1], self.pose_rc[0]), r, color='pink', fill=False))

    #             # get the point rounded to the nearest grid
    #             x = int(np.round(self.grid_position_xy[0] + r*np.sin(angle)))
    #             y = int(np.round(self.grid_position_xy[1] + r*np.cos(angle)))

    #             if x < 0 or x >= self.agent_map.shape[1] or y < 0 or y >= self.agent_map.shape[0]:
    #                 break
    #             sampled_point= self.ground_truth_map[y, x]
    #             if sampled_point == False:# obstacle
    #                 self.agent_map[y, x] = self.cfg.KNOWN_WALL
    #                 # ddraw the obstacle
    #                 if self.screen is not None:
    #                     pygame.draw.circle(self.screen, color= self.cfg.RED, center=(x*self.grid_size, y*self.grid_size), radius=5)

    #                 break
    #             if r == max(ray_cast_samples):# frontier
    #                 if self.agent_map[y, x] == self.cfg.KNOWN_EMPTY:
    #                     break
    #                 self.agent_map[y, x] = self.cfg.FRONTIER
    #                 if self.screen is not None:
    #                     pygame.draw.circle(self.screen, color=self.cfg.YELLOW, center=(x*self.grid_size, y*self.grid_size), radius=5)
    #                 break
    #             # free space
    #             self.agent_map[y, x] = self.cfg.KNOWN_EMPTY
    #             # pygame.draw.circle(self.screen, color= (0, 255, 0), center=(x, y), radius=self.grid_size//5)

    #         # draw lidar lines
    #         # pygame.draw.circle( self.screen, 
    #         #                     color=RED,
    #         #                     center=(self.grid_position[0]*self.grid_size, self.grid_position[1]*self.grid_size),
    #         #                     radius=self.grid_size//2)
    
    
    def save_to_mutual_data(self, mutual_data):
        if 'Agent_Data' not in mutual_data:
            mutual_data['Agent_Data'] = {} 
        if self.id not in mutual_data['Agent_Data']:
            mutual_data['Agent_Data'][self.id] = {}
        if 'help_request_list' not in mutual_data['Agent_Data'][self.id]:
            mutual_data['Agent_Data'][self.id]['help_request_list'] = []
        
        mutual_data['Agent_Data'][self.id]['plan'] = self.plan
        mutual_data['Agent_Data'][self.id]['goal_xy'] = self.goal_xy
        mutual_data['Agent_Data'][self.id]['grid_position_xy'] = self.grid_position_xy
        mutual_data['Agent_Data'][self.id]['choose_random'] = self.choose_random
        mutual_data['Agent_Data'][self.id]['disabled'] = self.disabled

        self.share_map(mutual_data['map'])

    def share_map(self, mutual_map):
        # 1st method will be to look at all the cells and chooses what to assine in the returned map
        for r,row in enumerate(mutual_map):
            for c, mutual_cell in enumerate(row):
                with self.lock:
                    cur_cell = self.agent_map[r,c]
                    if cur_cell == mutual_cell: 
                        continue
                    if cur_cell == self.cfg.KNOWN_EMPTY or mutual_cell == self.cfg.KNOWN_EMPTY:
                        mutual_map[r,c] = self.cfg.KNOWN_EMPTY
                        continue
                    if mutual_cell == self.cfg.UNKNOWN:
                        mutual_map[r,c] = cur_cell
                        # continue
                    # if cur_cell != mutual_cell:
                    #     mutual_map[r,c] = cur_cell

    def check_should_replan(self, mutual_data):

        # check if the plan is empty, if so replan
        if len(self.plan) <= 2:
            self.set_new_goal()
            return True
        
        else:
            for path_point in self.plan:
                if self.agent_map[path_point[1], path_point[0]] == self.cfg.KNOWN_WALL:
                    return True

        if self.goal_xy is None:
            self.set_new_goal()
            return True
        # check if the goal_xy is known to be empty, if so replan
        if self.agent_map[self.goal_xy[1], self.goal_xy[0]] == self.cfg.KNOWN_EMPTY or \
            self.agent_map[self.goal_xy[1], self.goal_xy[0]] == self.cfg.KNOWN_WALL:
            self.set_new_goal()
            return True

        # check if the goal_xy is reached, if so replan
        if (int(np.round(self.grid_position_xy[0])), int(np.round(self.grid_position_xy[1]))) == (self.goal_xy[0], self.goal_xy[1]):
            return True

        # NO need to replan
        return False
                    
    def update(self, mutual_data, draw=True):
        # Update the agent's position
        # Scan the environment
        self.scan()
        # Share the agent's map with the mutual map
        # self.share_map(mutual_data['map'])
        self.save_to_mutual_data(mutual_data)
        # Update the agent's map
        self.agent_map = mutual_data['map'].copy()

        if self.check_should_replan(mutual_data):
            self.replan(mutual_data)
            if self.area_completed:
                return 0, self.total_dist_traveled
            
        
        
        if self.plan is None: 
            self.plan = []
            warn_str = "❗️⭕️No plan == None to follow : " + self.__class__.__name__
            warnings.warn(warn_str) 
            return 0, self.total_dist_traveled
        
        if len(self.plan) == 0:
            warn_str = "❗️❌No plan len==0 to follow : " + self.__class__.__name__
            warnings.warn(warn_str )
            return 0, self.total_dist_traveled
            
        self.move(mutual_data)
        # self.draw()
        if draw:
            self.draw()
        
        # trade goal_xy with other agents
        return len(self.plan), self.total_dist_traveled
