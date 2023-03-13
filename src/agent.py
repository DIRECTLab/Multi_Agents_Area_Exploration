# this hold the agent class

import random
import math
import pygame
import numpy as np
import matplotlib.pyplot as plt
import warnings
from src.planners.astar_new import astar
from src.replan.rand_horizen import *
from src.replan.voronoi_random import *

def createBot(base =None):
    # # Rand_Frontier
    # # Rand_Voronoi
    # Closest_Voronoi
    class Agent(base):
        def __init__(self, 
                    cfg,
                    id, 
                    body_size,
                    grid_size,
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

            if goal_xy is None:
                self.goal_xy = self.get_random_point()
            else:
                self.goal_xy = goal_xy
            if position is None:
                self.grid_position_xy = self.get_random_point()
            else:
                self.grid_position_xy = position

            self.ax = ax
            self.screen = screen

            self.lock = lock
            # Start at 0 velocity
            self.dx= 0
            self.dy= 0
            self.total_dist_traveled = 0
            self.past_traversed_locations =[self.grid_position_xy]

            # scan the map and build the map
            self.scan()
            self.replan()
            
        def get_random_point(self):
            # make sure the goal is not in the obstacle
            while True:
                point_rc = (np.random.randint(self.ground_truth_map.shape[0]), np.random.randint(self.ground_truth_map.shape[1]))
                if self.ground_truth_map[point_rc] == self.cfg.EMPTY:
                    point_xy = (point_rc[1], point_rc[0])
                    break
            return point_xy
        
        def get_closest_point_rc(self, pointlist):
            min_dist = np.inf
            min_point = None
            for point_rc in pointlist:
                dist = np.sqrt((point_rc[1] - self.grid_position_xy[0])**2 + (point_rc[0] - self.grid_position_xy[1])**2)
                if dist < min_dist:
                    min_dist = dist
                    min_point = point_rc
            return min_point
        
        def set_new_goal(self):
            self.goal_xy = self.get_goal_method()
            assert self.goal_xy != self.grid_position_xy, "Goal and position are the same"
            

        def replan(self):
            if self.area_completed:
                return
            self.replan_count += 1
            # # check id the goal_xy is known
            self.plan = astar(  np.where(self.agent_map == self.cfg.KNOWN_WALL, self.cfg.KNOWN_WALL, self.cfg.KNOWN_EMPTY), 
                                (int(np.round(self.grid_position_xy[0])), int(np.round(self.grid_position_xy[1]))),
                                self.goal_xy)
            if self.plan == None:
                if self.replan_count > 100:
                    warnings.warn("Replan count is too high")
                assert self.replan_count < 200, "Replan count is too high 200"

                self.set_new_goal()
                self.replan()
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


        def move(self):
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
            for i, angle in enumerate(np.arange(0, 2*np.pi, self.lidar_sweep_res)):

                x, y = self.grid_position_xy

                ray_cast_samples = np.arange(0,self.lidarRange, self.lidar_step_res)
                for j, r in enumerate(ray_cast_samples):
                    # self.world_ax.add_patch(plt.Circle((self.pose_rc[1], self.pose_rc[0]), r, color='pink', fill=False))

                    # get the point rounded to the nearest grid
                    x = int(np.round(self.grid_position_xy[0] + r*np.sin(angle)))
                    y = int(np.round(self.grid_position_xy[1] + r*np.cos(angle)))

                    if x < 0 or x >= self.agent_map.shape[1] or y < 0 or y >= self.agent_map.shape[0]:
                        break
                    sampled_point= self.ground_truth_map[y, x]
                    if sampled_point == False:# obstacle
                        self.agent_map[y, x] = self.cfg.KNOWN_WALL
                        # ddraw the obstacle
                        if self.screen is not None:
                            pygame.draw.circle(self.screen, color= self.cfg.RED, center=(x*self.grid_size, y*self.grid_size), radius=self.grid_size//2)

                        break
                    if r == max(ray_cast_samples):# frontier
                        if self.agent_map[y, x] == self.cfg.KNOWN_EMPTY:
                            break
                        self.agent_map[y, x] = self.cfg.FRONTIER
                        if self.screen is not None:
                            pygame.draw.circle(self.screen, color=self.cfg.YELLOW, center=(x*self.grid_size, y*self.grid_size), radius=self.grid_size//2)
                        break
                    # free space
                    self.agent_map[y, x] = self.cfg.KNOWN_EMPTY
                    # pygame.draw.circle(self.screen, color= (0, 255, 0), center=(x, y), radius=self.grid_size//5)

                # draw lidar lines
                # pygame.draw.circle( self.screen, 
                #                     color=RED,
                #                     center=(self.grid_position[0]*self.grid_size, self.grid_position[1]*self.grid_size),
                #                     radius=self.grid_size//2)

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

        def check_should_replan(self):
            # check if the plan is empty, if so replan
            if len(self.plan) <= 2:
                self.set_new_goal()
                return True
            else:
                for path_point in self.plan:
                    if self.agent_map[path_point[1], path_point[0]] == self.cfg.KNOWN_WALL:
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
                        
        def update(self, mutual_map, draw=True):
            if self.area_completed:
                return 0, self.total_dist_traveled
            # Update the agent's position
            # Scan the environment
            self.scan()
            # Share the agent's map with the mutual map
            self.share_map(mutual_map)
            # Update the agent's map
            self.agent_map = mutual_map.copy()



            if self.check_should_replan():
                self.replan()
                if self.area_completed:
                    return 0, self.total_dist_traveled
                
            self.move()
            # self.draw()
            if draw:
                self.draw()
            
            # trade goal_xy with other agents
            return len(self.plan), self.total_dist_traveled

    return Agent