# this hold the agent class

import random
import pygame
import numpy as np
import matplotlib.pyplot as plt

from src.planners.astar import astar
from src.config import *

# https://stackoverflow.com/a/40372261/9555123
def custom_round(x, base=5):
    return int(base * round(float(x)/base))

class Agent():
    def __init__(self, 
                 id, 
                 body_size,
                 grid_size,
                 lidar_range, 
                 full_map,
                 position=(10, 10),
                 goal=None,
                 color=(0,255,0),
                 ax=None,
                 screen=None):
        self.id = id
        self.body_size = body_size
        self.grid_size = grid_size
        self.full_map = full_map.copy()
        self.agent_map = - np.ones((full_map.shape[0], full_map.shape[1])).astype(int)
        self.grid_position = position
        self.cur_color = color
        self.lidarRange = lidar_range
        self.lidar_sweep_res = (np.arctan2(1, self.lidarRange)%np.pi ) * 2
        self.lidar_step_res = 1
        if goal is None:
            self.goal = self.get_random_goal()
        else:
            self.goal = goal

        self.ax = ax
        self.screen = screen
        # randomize the 
        self.dx= np.random.rand()/1
        self.dy= np.random.rand()/1

        # scan the map and build the map
        self.scan()



        self.plan = astar(list(np.where(self.agent_map == 1, 0, 1)), 
                            self.grid_position, 
                            self.goal)


    def get_random_goal(self):
        # make sure the goal is not in the obstacle
        while True:
            goal = (np.random.randint(self.full_map.shape[0]), np.random.randint(self.full_map.shape[1]))
            if self.full_map[goal] == True:
                break
        return goal

    def draw(self):    
        # draw the agent, only when rendering do we need to use self.grid_size to scale the position
        pygame.draw.circle(self.screen, color= self.cur_color, 
                           center=(self.grid_position[0]* self.grid_size,self.grid_position[1]* self.grid_size),
                            radius=self.body_size)
        # draw line to goal
        pygame.draw.circle( self.screen, 
                            color= (0, 255, 0), 
                            center=(self.goal[0]* self.grid_size,self.goal[1]* self.grid_size),
                            radius=self.grid_size//2
                        )

        # update plt plot
        self.ax.matshow(self.agent_map)
        self.ax.plot(self.grid_position[0], self.grid_position[1], markersize=1, marker='.', color=np.array(self.cur_color)/255)

    

    def move(self, ):
        # Update the agent's position
        cur_x = self.grid_position[0]
        cur_y = self.grid_position[1]

        # next_path_point = self.plan[0]
        # if (int(np.round(cur_x)), int(np.round(cur_y))) == (next_path_point[0], next_path_point[1]):
        #     # get the next point
        #     self.plan.pop(0)
        #     next_path_point = self.plan[0]

        if (int(np.round(cur_x)), int(np.round(cur_y))) == (self.goal[0], self.goal[1]):
            # get the next point
            self.goal = self.get_random_goal()
            # self.plan = astar(list(np.where(self.built_map == 1, 0, 1)),
            #                     self.grid_position,
            #                     self.goal)
            return
        else:
            # get the direction from current position to next point
            #  scale such that the sum of the squares of the components is velocity
            velocity = 1
            self.dx = velocity * (self.goal[0] - cur_x) / np.sqrt((self.goal[0] - cur_x)**2 + (self.goal[1] - cur_y)**2)
            self.dy = velocity * (self.goal[1] - cur_y) / np.sqrt((self.goal[0] - cur_x)**2 + (self.goal[1] - cur_y)**2)

            # get the next point from the plan
            
            # self.dx = velocity * (next_path_point[0] - cur_x) / np.sqrt((next_path_point[0] - cur_x)**2 + (next_path_point[1] - cur_y)**2)
            # self.dy = velocity * (next_path_point[1] - cur_y) / np.sqrt((next_path_point[0] - cur_x)**2 + (next_path_point[1] - cur_y)**2)

        new_position = (self.grid_position[0] + self.dx, self.grid_position[1] + self.dy)
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
        sampled_next_point = self.full_map[int(np.round(new_y)), int(np.round(new_x))]
        if sampled_next_point == False:# obstacle
            # move in the direction from sampeld_point to position
            self.dx *= -1
            self.dy *= -1
            # throw an error
            # raise Exception("Agent collided with obstacle")
        
        self.grid_position = new_position

    def scan(self):
        # send out scan to update local built_map
        for i, angle in enumerate(np.arange(0, 2*np.pi, self.lidar_sweep_res)):

            x, y = self.grid_position

            ray_cast_samples = np.arange(0,self.lidarRange, self.lidar_step_res)
            for j, r in enumerate(ray_cast_samples):
                # self.world_ax.add_patch(plt.Circle((self.pose_rc[1], self.pose_rc[0]), r, color='pink', fill=False))

                # get the point rounded to the nearest grid
                x = int(np.round(self.grid_position[0] + r*np.sin(angle)))
                y = int(np.round(self.grid_position[1] + r*np.cos(angle)))

                if x < 0 or x >= self.agent_map.shape[1] or y < 0 or y >= self.agent_map.shape[0]:
                    break
                sampled_point= self.full_map[y, x]
                if sampled_point == False:# obstacle
                    self.agent_map[y, x] = KNOWN_WALL
                    # ddraw the obstacle
                    pygame.draw.circle(self.screen, color= (255, 0, 0), center=(x*self.grid_size, y*self.grid_size), radius=self.grid_size//2)

                    break
                if r == max(ray_cast_samples):# frontier
                    if self.agent_map[y, x] == KNOWN_EMPTY:
                        break
                    self.agent_map[y, x] = FRONTIER
                    pygame.draw.circle(self.screen, color=(255, 255, 0), center=(x*self.grid_size, y*self.grid_size), radius=self.grid_size//2)
                    break
                # free space
                self.agent_map[y, x] = KNOWN_EMPTY
                # pygame.draw.circle(self.screen, color= (0, 255, 0), center=(x, y), radius=self.grid_size//5)

            # draw lidar lines
            pygame.draw.circle( self.screen, 
                                color=(0, 0, 255),
                                center=(self.grid_position[0]*self.grid_size, self.grid_position[1]*self.grid_size),
                                radius=self.grid_size//2
                            )
    def share_map(self, mutual_map):
        # 1st method will be to look at all the cells and chooses what to assine in the returned map
        for r,row in enumerate(mutual_map):
            for c, mutual_cell in enumerate(row):
                cur_cell = self.agent_map[r,c]
                if cur_cell == mutual_cell: #Frontier
                    continue
                if mutual_cell == UNKNOWN:
                    mutual_map[r,c] = cur_cell
                    # continue
                # if cur_cell != mutual_cell:
                #     mutual_map[r,c] = cur_cell
                
                    
    def update(self, mutual_map, draw=True):
        # Update the agent's position

        self.scan()
        self.share_map(mutual_map)
        self.move()
        # self.draw()
        if draw:
            self.draw()
        
        # trade goal with other agents
