# this hold the agent class

import random
import pygame
import numpy as np

from astar import AStarPlanner


class Agent(AStarPlanner):
    def __init__(self, body_size, lidar_range, empty_map, position=(100, 100) ):
        self.body_size = body_size
        self.lidar_range = lidar_range
        self.map = empty_map.copy()
        self.position = position
        self.cur_color = (random.randint(0, 255), random.randint(0, 255), 0)

        # randomize the 
        self.dx= np.random.rand()/10
        self.dy= np.random.rand()/10
        AStarPlanner.__init__(self, self.map, self.body_size)

    def draw(self, screen):    
        # draw the agent
        pygame.draw.circle(screen, color= self.cur_color, center=self.position, radius=self.body_size)

    def move(self, ):
        # Update the agent's position
        new_position = (self.position[0] + self.dx, self.position[1] + self.dy)
        if new_position[0] < 0 or new_position[0] >= self.map.shape[0]:
            return 
        if new_position[1] < 0 or new_position[1] >= self.map.shape[1]:
            return
        
        self.position = new_position

    def scan(self, ):
        # send out scan to update local map

    def update(self, map):
        # Update the agent's position
        self.move()
        