# this hold the agent class

import random
import math
import pygame
import numpy as np
import matplotlib.pyplot as plt
import warnings
from src.planners.astar_new import astar
# from src.replan.choose_random import *
# from src.replan.voronoi_choose_random import *


class Point_Finding:
    def get_random_point(self):
        index_list = list(np.argwhere(self.ground_truth_map == self.cfg.EMPTY))
        # shuffle the list
        random.shuffle(index_list,)
        # get the first point
        point_xy = (index_list[0][1], index_list[0][0])
        return point_xy

    
    def get_closest_point_rc(self, pointlist):
        '''
        This function returns the closest point from the pointlist to the agent
        :param pointlist: a list of points (r,c)
        :return: the closest point from the pointlist to the agent
        '''
        min_dist = np.inf
        min_point = None
        for point_rc in pointlist:
            dist = np.sqrt((point_rc[1] - self.grid_position_xy[0])**2 + (point_rc[0] - self.grid_position_xy[1])**2)
            if dist < min_dist:
                min_dist = dist
                min_point = point_rc
        if min_point is None:
            raise Exception("min_point is None")
        return min_point
    
    def get_new_location_xy(self,map_area,  MapLocationType = None, useRandom = False):
        '''
        This function returns a random location from the map_area
        :param map_area: the map area to choose from typically self.agent_map
        :param MapLocationType: the type of location to choose from: self.cfg.FRONTIER or self.cfg.UNKNOWN
        :return: a random location from the map_area (x,y) or None if no location is found
        '''
        if MapLocationType ==None:
            raise Exception("MapLocationType is None set it to self.cfg.FRONTIER or self.cfg.UNKNOWN")
        if len(map_area) == 0:
            return None
        
        if map_area[0].shape == (2,):
            points_array = map_area 
        else:
            points_array = np.argwhere(map_area == MapLocationType)
        
        if len(points_array) == 0:
            return None
        elif len(points_array) == 1:
            return (points_array[0][1], points_array[0][0])
        
        if useRandom:
            # choose a random point
            idx = np.random.randint(len(points_array))
            return (points_array[idx][1], points_array[idx][0])

        point = self.get_closest_point_rc(list(points_array))
        return (point[1], point[0])
    
    
class Agent(Point_Finding):
    def __init__(self, 
                cfg,
                id, 
                body_size,
                grid_size,
                lidar_range, 
                full_map,
                assigned_points =None,
                # position=None,
                # goal_xy=None,
                color=(0,255,0),
                ax=None,
                screen=None,
                lock = None,
                required_explore = 0.5):
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

        self.goal_xy = None
        self.grid_position_xy = None
        # Base Class will set the goal
        self.choose_start_position()
        assert self.grid_position_xy is not None, "grid_position_xy is None, the Base method is not implemented"
        self.choose_start_goal()
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
        self.explored_sufficiently = False
        self.required_explore = required_explore
        self.personal_explored_area = 0

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
            # assert self.replan_count < self.agent_map.size, f"Replan count is too high {self.agent_map.size}"

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
        prev_explored_area = self.calculate_personal_searched_area()
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

        self.personal_explored_area += self.calculate_personal_searched_area() - prev_explored_area
    
    def save_to_mutual_data(self, mutual_data):
        if 'Agent_Data' not in mutual_data:
            mutual_data['Agent_Data'] = {} 
        if self.id not in mutual_data['Agent_Data']:
            mutual_data['Agent_Data'][self.id] = {}
        if 'help_request_list' not in mutual_data['Agent_Data'][self.id]:
            mutual_data['Agent_Data'][self.id]['help_request_list'] = []
        if 'personal_explored_area' not in mutual_data['Agent_Data'][self.id]:
            mutual_data['Agent_Data'][self.id]['personal_explored_area'] = []
        if 'total_explored_area' not in mutual_data:
            mutual_data['total_explored_area'] = []
        
        mutual_data['Agent_Data'][self.id]['plan'] = self.plan
        mutual_data['Agent_Data'][self.id]['goal_xy'] = self.goal_xy
        mutual_data['Agent_Data'][self.id]['grid_position_xy'] = self.grid_position_xy
        mutual_data['Agent_Data'][self.id]['choose_random'] = self.choose_random
        mutual_data['Agent_Data'][self.id]['disabled'] = self.disabled
        mutual_data['Agent_Data'][self.id]['personal_explored_area'].append(self.personal_explored_area)
        mutual_data['Agent_Data'][self.id]['personal_map'] = self.agent_map.copy()

        num_bots = self.cfg.N_BOTS
        for i in range(num_bots):
            if i == self.id or i not in mutual_data['Agent_Data']:
                continue
            dist = np.sqrt((mutual_data['Agent_Data'][i]['grid_position_xy'][0] - self.grid_position_xy[0])**2 + (mutual_data['Agent_Data'][i]['grid_position_xy'][1] - self.grid_position_xy[1])**2)
            if dist < 5:
                self.share_map(mutual_data['Agent_Data'][i]['personal_map'])
        
        if self.id == 0:
            total_explored_area = (np.sum(mutual_data['map'] == self.cfg.KNOWN_EMPTY) + np.sum(mutual_data['map'] == self.cfg.KNOWN_WALL)) / mutual_data['map'].size
            mutual_data['total_explored_area'].append(total_explored_area)

            if 'group_exploration_stop' not in mutual_data['Agent_Data']:
                mutual_data['Agent_Data']['group_exploration_stop'] = .01
            exploration_stop = mutual_data['Agent_Data']['group_exploration_stop']
            for i in range(num_bots):
                if i == self.id or i not in mutual_data['Agent_Data']:
                    continue
                if mutual_data['Agent_Data'][i]['personal_explored_area'][-1] < exploration_stop:
                    break
                if(i == num_bots - 1):
                    mutual_data['Agent_Data']['group_exploration_stop'] = exploration_stop + .01
                    if 'total_explored_at_point' not in mutual_data['Agent_Data']:
                        mutual_data['Agent_Data']['total_explored_at_point'] = []
                        mutual_data['Agent_Data']['total_explored_at_point'].append([exploration_stop, mutual_data['total_explored_area'][-1]])

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
    
    def should_continue_searching(self, mutual_data):
        if 'Agent_Data' not in mutual_data:
            return True
        if self.id not in mutual_data['Agent_Data']:
            return True
        if 'personal_explored_area' not in mutual_data['Agent_Data'][self.id]:
            return True
        if 'group_exploration_stop' not in mutual_data['Agent_Data']:
            return True
        if mutual_data['Agent_Data'][self.id]['personal_explored_area'][-1] > mutual_data['Agent_Data']['group_exploration_stop']:
            return False
        return True

    def calculate_personal_searched_area(self):
        # calculate the area the agent has searched
        explored_area = np.sum(self.agent_map == self.cfg.KNOWN_EMPTY) + np.sum(self.agent_map == self.cfg.KNOWN_WALL)
        explored_area /= self.agent_map.size
        return explored_area
                    
    def update(self, mutual_data, draw=True):
        if 'Agent_Data' in mutual_data and self.id in mutual_data['Agent_Data'] and 'personal_map' in mutual_data['Agent_Data'][self.id]:
            self.agent_map = mutual_data['Agent_Data'][self.id]['personal_map']
        
        # Update the agent's position
        # Scan the environment
        self.scan()
        # Share the agent's map with the mutual map
        # self.share_map(mutual_data['map'])
        self.save_to_mutual_data(mutual_data)
        # Update the agent's map
        # self.agent_map = mutual_data['map'].copy()
        if(not self.should_continue_searching(mutual_data)):
            return 0, self.total_dist_traveled

        if self.check_should_replan(mutual_data):
            self.replan(mutual_data)
            if self.area_completed:
                return 0, self.total_dist_traveled
            
        if self.personal_explored_area >= self.required_explore / 100:
            self.area_completed = True
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
