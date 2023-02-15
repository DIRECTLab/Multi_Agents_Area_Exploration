# this hold the agent class

import random
import pygame
import numpy as np

class Agent:
    def __init__(self,screen, body_size, lidar_range, empty_map):
        self.body_size = body_size
        self.lidar_range = lidar_range
        self.map = empty_map.copy()
        self.position = (0, 0)
        self.cur_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
    def draw(self, ):    
        # draw the agent
        pygame.draw.circle(screen, color= cur_color, center=(0, 0), radius=body_size)

    def move(self, dx, dy):
        # Update the agent's position
        self.position = (self.position[0] + dx, self.position[1] + dy)

        # TODO: Implement agent movement
        pass

    def sense(self, walls, openings):
        # Update the map based on the agent's position
        px, py = self.position
        x_min = max(0, int((px - self.lidar_range) / self.map_resolution))
        x_max = min(self.map_width - 1, int((px + self.lidar_range) / self.map_resolution))
        y_min = max(0, int((py - self.lidar_range) / self.map_resolution))
        y_max = min(self.map_height - 1, int((py + self.lidar_range) / self.map_resolution))

        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                # Calculate the distance from the agent to the current cell
                cell_center = ((x + 0.5) * self.map_resolution, (y + 0.5) * self.map_resolution)
                dist = np.sqrt((px - cell_center[0]) ** 2 + (py - cell_center[1]) ** 2)

                # Check if there is a wall or opening in the way
                obstructed = False
                for wall in walls:
                    if wall.collidepoint(cell_center):
                        obstructed = True
                        break
                for opening in openings:
                    if opening.collidepoint(cell_center):
                        obstructed = False
                        break

                # Update the map based on the LIDAR reading
                if not obstructed and dist <= self.lidar_range:
                    self.map[y][x] = 1
                else:
                    self.map[y][x] = 0
