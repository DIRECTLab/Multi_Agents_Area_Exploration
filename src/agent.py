# this hold the agent class

import random 
import math
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
                 position=None,
                 goal=None,
                 color=(0,255,0),
                 ax=None,
                 screen=None):
        self.id = id
        self.body_size = body_size
        self.grid_size = grid_size
        self.full_map = full_map.copy()
        self.agent_map = - np.ones((full_map.shape[0], full_map.shape[1])).astype(int)
        self.cur_color = color
        self.lidarRange = lidar_range
        self.lidar_sweep_res = (np.arctan2(1, self.lidarRange)%np.pi ) * 2
        self.lidar_step_res = 1
        if goal is None:
            self.goal = self.get_random_point()
        else:
            self.goal = goal
        if position is None:
            self.grid_position = self.get_random_point()
        else:
            self.grid_position = position

        self.ax = ax
        self.screen = screen
        # Start at 0 velocity
        self.dx= 0
        self.dy= 0

        # scan the map and build the map
        self.scan()
        self.replan()





    def get_random_point(self):
        # make sure the goal is not in the obstacle
        while True:
            goal = (np.random.randint(self.full_map.shape[0]), np.random.randint(self.full_map.shape[1]))
            if self.full_map[goal] == True:
                break
        return goal
    
    def replan(self):
        # self.plan = astar(list(np.where(self.agent_map == KNOWN_WALL, 1, 0)), 
        #                     (int(np.round(self.grid_position[0])), int(np.round(self.grid_position[1]))),
        #                     self.goal,
        #                     allow_diagonal_movement=True,)
        self.plan = astar(np.where(self.agent_map == KNOWN_WALL, KNOWN_WALL, KNOWN_EMPTY), 
                            (int(np.round(self.grid_position[0])), int(np.round(self.grid_position[1]))),
                            self.goal,
                            allow_diagonal_movement=True,)
        if type(self.plan) != list:
            self.plan = []

        # remove the current position
        if len(self.plan) > 0:
            self.plan.pop(0)
    
    # def draw_arrow(self, start, end, head_width =2, line_width = 2, color=RED, width=1):
    #     # Calculate the angle of the arrow
    #     # angle = np.atan2(end[1]-start[1], end[0]-start[0])
    #     angle = np.arctan2(end[1]-start[1], end[0]-start[0])

    #     # Calculate the length of the arrow line
    #     length = np.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)

    #     # Calculate the size of the arrow head based on the line width
    #     head_size = int(head_width * line_width)

    #     # Create a surface to draw the arrow on
    #     arrow_surface = pygame.Surface((length, head_size), pygame.SRCALPHA)
        
    #     # transform the surface to the correct angle
    #     arrow_surface = pygame.transform.rotate(arrow_surface, np.rad2deg(angle))

    #     # Draw the arrow line
    #     pygame.draw.line(arrow_surface, color, (0, line_width//2), (length, line_width//2), line_width)

    def arrow( self, lcolor, tricolor, start, end, trirad, thickness=2):
        rad = math.pi/180
        pygame.draw.line(self.screen, lcolor, start, end, thickness)
        rotation = (math.atan2(start[1] - end[1], end[0] - start[0])) + math.pi/2
        # pygame.draw.polygon(self.screen, tricolor, ((end[0] + trirad * math.sin(rotation),
        #                                     end[1] + trirad * math.cos(rotation)),
        #                                 (end[0] + trirad * math.sin(rotation - 120*rad),
        #                                     end[1] + trirad * math.cos(rotation - 120*rad)),
        #                                 (end[0] + trirad * math.sin(rotation + 120*rad),
        #                                     end[1] + trirad * math.cos(rotation + 120*rad))))

        # acute triangle
        pygame.draw.polygon(self.screen, tricolor, 
            ((end[0] + trirad * math.sin(rotation), end[1] + trirad * math.cos(rotation)),
            (end[0] + trirad * math.sin(rotation - 90*rad),end[1] + trirad * math.cos(rotation - 90*rad)),
            (end[0] + trirad * math.sin(rotation + 90*rad),end[1] + trirad * math.cos(rotation + 90*rad))))

    def draw(self):    
        # draw the agent, only when rendering do we need to use self.grid_size to scale the position
        # pygame.draw.circle(self.screen, color= self.cur_color, 
        #                    center=(self.grid_position[0]* self.grid_size,self.grid_position[1]* self.grid_size),
        #                     radius=self.body_size)

        # draw line to goal
        # pygame.draw.line(self.screen, color= TEAL,
        #                     start_pos=(self.grid_position[0]* self.grid_size,self.grid_position[1]* self.grid_size),
        #                     end_pos=(self.goal[0]* self.grid_size,self.goal[1]* self.grid_size),
        #                     width=self.grid_size//2)


        # draw an arrow in the direction of dx, dy
        # self.draw_arrow((self.grid_position[0]* self.grid_size,self.grid_position[1]* self.grid_size),
        #                 (self.grid_position[0]* self.grid_size + self.dx * self.grid_size,
        #                 self.grid_position[1]* self.grid_size + self.dy * self.grid_size))
        self.arrow(BLUE, 
                    YELLOW, 
                    (self.grid_position[0]* self.grid_size,self.grid_position[1]* self.grid_size),
                    (self.grid_position[0]* self.grid_size + self.dx * self.grid_size,
                    self.grid_position[1]* self.grid_size + self.dy * self.grid_size),
                    10)

        # update plt plot
        # clear the plot
        self.ax.clear()
        self.ax.matshow(self.agent_map)
        self.ax.plot(self.grid_position[0], self.grid_position[1], markersize=1, marker='.', color=np.array(self.cur_color)/255)

        # draw the plan line in pygame
        if len(self.plan) > 0:
            for i in range(len(self.plan)-1):
                pygame.draw.line(self.screen, color= GREEN,
                                start_pos=(self.plan[i][0]* self.grid_size,self.plan[i][1]* self.grid_size),
                                end_pos=(self.plan[i+1][0]* self.grid_size,self.plan[i+1][1]* self.grid_size),
                                width=self.grid_size//4)
                # draw plt line
                self.ax.plot([self.plan[i][0], self.plan[i+1][0]], [self.plan[i][1], self.plan[i+1][1]], color=np.array(GREEN)/255)



    def move(self, ):
        # Update the agent's position
        cur_x = self.grid_position[0]
        cur_y = self.grid_position[1]


        if (int(np.round(cur_x)), int(np.round(cur_y))) == (self.goal[0], self.goal[1]):
            # get the next point
            self.goal = self.get_random_point()
            self.replan()
            return
        
        if len(self.plan) == 0:
            # get the next point
            self.goal = self.get_random_point()
            self.replan()
            return
        
        next_path_point = self.plan[0]
        if (int(np.round(cur_x)), int(np.round(cur_y))) == (next_path_point[0], next_path_point[1]):
            # get the next point
            self.plan.pop(0)
            next_path_point = self.plan[0]
        else:
            # get the direction from current position to next point
            #  scale such that the sum of the squares of the components is velocity
            velocity = 1
            # self.dx = velocity * (self.goal[0] - cur_x) / np.sqrt((self.goal[0] - cur_x)**2 + (self.goal[1] - cur_y)**2)
            # self.dy = velocity * (self.goal[1] - cur_y) / np.sqrt((self.goal[0] - cur_x)**2 + (self.goal[1] - cur_y)**2)
            # draw a line to the next point

            # pygame.draw.line(self.screen, color= GREEN,
            #                     start_pos=(cur_x* self.grid_size,cur_y* self.grid_size),
            #                     end_pos=(next_path_point[0]* self.grid_size,next_path_point[1]* self.grid_size),
            #                     width=self.grid_size//2)
            # move towards the next point
            direction = (next_path_point[0] - cur_x, next_path_point[1] - cur_y)
            self.dx = velocity * direction[0] / np.sqrt(direction[0]**2 + direction[1]**2)
            self.dy = velocity * direction[1] / np.sqrt(direction[0]**2 + direction[1]**2)


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
                    pygame.draw.circle(self.screen, color= RED, center=(x*self.grid_size, y*self.grid_size), radius=self.grid_size//2)

                    break
                if r == max(ray_cast_samples):# frontier
                    if self.agent_map[y, x] == KNOWN_EMPTY:
                        break
                    self.agent_map[y, x] = FRONTIER
                    pygame.draw.circle(self.screen, color=YELLOW, center=(x*self.grid_size, y*self.grid_size), radius=self.grid_size//2)
                    break
                # free space
                self.agent_map[y, x] = KNOWN_EMPTY
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
        # self.agent_map = mutual_map.copy()
        self.replan()
        
        self.move()
        # self.draw()
        if draw:
            self.draw()
        
        # trade goal with other agents
