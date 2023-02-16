# this hold the agent class

import random
import pygame
import numpy as np

from astar import AStarPlanner

# https://stackoverflow.com/a/40372261/9555123
def custom_round(x, base=5):
    return int(base * round(float(x)/base))

class Agent(AStarPlanner):
    def __init__(self, body_size, grid_size, lidar_range, full_map, position=(100, 100) ):
        self.body_size = body_size
        self.grid_size = grid_size
        self.full_map = full_map.copy()
        self.built_map = np.zeros((full_map.shape[0], full_map.shape[1])).astype(int)
        self.position = position
        self.cur_color = (random.randint(0, 255), random.randint(0, 255), 0)

        # randomize the 
        self.dx= np.random.rand()/10
        self.dy= np.random.rand()/10
        AStarPlanner.__init__(self, self.full_map, self.grid_size)

        self.lidarRange = lidar_range
        self.lidar_sweep_res = (np.arctan2(self.grid_size, self.lidarRange)%np.pi ) * 2
        self.lidar_step_res = self.grid_size//2

    def draw(self, screen):    
        # draw the agent
        pygame.draw.circle(screen, color= self.cur_color, center=self.position, radius=self.body_size)

        # draw lidar range


    def move(self, ):
        # Update the agent's position
        new_position = (self.position[0] + self.dx, self.position[1] + self.dy)
        if new_position[0] < 0 or new_position[0] >= self.built_map.shape[0]:
            return 
        if new_position[1] < 0 or new_position[1] >= self.built_map.shape[1]:
            return
        
        self.position = new_position

    def scan(self,screen ):
        # send out scan to update local built_map
        for i, angle in enumerate(np.arange(0, 2*np.pi, self.lidar_sweep_res)):

            x, y = self.position

            ray_cast_samples = np.arange(0,self.lidarRange, self.lidar_step_res)
            for j, r in enumerate(ray_cast_samples):
                # self.world_ax.add_patch(plt.Circle((self.pose_rc[1], self.pose_rc[0]), r, color='pink', fill=False))

                # get the point rounded to the nearest grid
                x = int(custom_round(self.position[0] + r*np.sin(angle), base=self.grid_size))
                y = int(custom_round(self.position[1] + r*np.cos(angle), base=self.grid_size))

                if x < 0 or x >= self.built_map.shape[1] or y < 0 or y >= self.built_map.shape[0]:
                    break
                sampled_point= self.full_map[y, x]
                if sampled_point == False:# obstacle
                    self.built_map[y, x] = 1
                    # ddraw the obstacle
                    pygame.draw.circle(screen, color= (255, 0, 0), center=(x, y), radius=self.grid_size//2)
                    break
                if r == max(ray_cast_samples):# frontier
                    self.built_map[y, x] = 2
                    pygame.draw.circle(screen, color= (0, 0, 255), center=(x, y), radius=self.grid_size//2)
                    break
                # if sampled_point == True:# free space
                self.built_map[y, x] = 0
                # pygame.draw.circle(screen, color= (0, 255, 0), center=(x, y), radius=self.grid_size//5)

            pygame.draw.line(screen, color= (255, 0, 0), 
                             start_pos=(self.position[0], self.position[1]), 
                             end_pos=(x, y),
                                width=1)

    def update(self, built_map, screen):
        # Update the agent's position

        self.move()
        self.scan(screen)
        self.draw(screen)
        