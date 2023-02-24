# this hold the agent class

import random
import pygame
import numpy as np
import matplotlib.pyplot as plt

import src.world
from src.astar import AStarPlanner

# https://stackoverflow.com/a/40372261/9555123
def custom_round(x, base=5):
    return int(base * round(float(x)/base))

class Agent(AStarPlanner):
    def __init__(self, 
            id, body_size, grid_size, lidar_range, 
            full_map, position=(10, 10),
            goal=None, color=(random.randint(0, 255), random.randint(0, 255), 0),
            ax=None,screen=None):
        self.id = id
        self.body_size = body_size
        self.grid_size = grid_size
        self.full_map = full_map.copy()
        self.built_map = np.zeros((full_map.shape[0], full_map.shape[1])).astype(int)
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
        # # plan the path
        # super(Agent, self).__init__(map= np.where(self.built_map == 1, True, False))
        # # plan is a list of tuples points
        # self.plan = self.planning(sx = self.grid_position[0], sy = self.grid_position[1],
        #                gx = self.goal[0], gy = self.goal[1])
        self.plan = []


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
        pygame.draw.line(self.screen, color= (0, 255, 0), 
                         start_pos=(self.grid_position[0]* self.grid_size,self.grid_position[1]* self.grid_size), 
                         end_pos=(self.goal[0]* self.grid_size,self.goal[1]* self.grid_size), width=5)

        # update plt plot
        self.ax.matshow(self.built_map)
        self.ax.plot(self.grid_position[0], self.grid_position[1], markersize=1, marker='.', color=np.array(self.cur_color)/255)

    

    def move(self, ):
        # Update the agent's position
        cur_x = self.grid_position[0]
        cur_y = self.grid_position[1]

        if (int(np.round(cur_x)), int(np.round(cur_y))) == (self.goal[0], self.goal[1]):
            # get the next point
            self.goal = self.get_random_goal()
        #     # update the plan
        #     self.plan = self.planning(sx = int(np.round(cur_x)), sy =  int(np.round(cur_y)),
        #                   gx = self.goal[0], gy = self.goal[1])
        #     return
        # elif (int(np.round(cur_x)), int(np.round(cur_y))) == self.plan[0]:
        #     # remove the point from the plan
        #     self.plan.pop(0)
            return
        else:
            # get the direction from current position to next point
            #  scale such that the sum of the squares of the components is velocity
            velocity = 1
            self.dx = velocity * (self.goal[0] - cur_x) / np.sqrt((self.goal[0] - cur_x)**2 + (self.goal[1] - cur_y)**2)
            self.dy = velocity * (self.goal[1] - cur_y) / np.sqrt((self.goal[0] - cur_x)**2 + (self.goal[1] - cur_y)**2)

            # # get the next point from the plan
            # next_point = self.plan[0]
            # self.dx = velocity * (next_point[0] - cur_x) / np.sqrt((next_point[0] - cur_x)**2 + (next_point[1] - cur_y)**2)
            # self.dy = velocity * (next_point[1] - cur_y) / np.sqrt((next_point[0] - cur_x)**2 + (next_point[1] - cur_y)**2)

        new_position = (self.grid_position[0] + self.dx, self.grid_position[1] + self.dy)
        new_x = new_position[0]
        new_y = new_position[1]

        # boundary collision
        if new_x < 0 or new_x >= self.built_map.shape[0]:
            self.dx *= -1
            return 
        if new_y < 0 or new_y >= self.built_map.shape[1]:
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

                if x < 0 or x >= self.built_map.shape[1] or y < 0 or y >= self.built_map.shape[0]:
                    break
                sampled_point= self.full_map[y, x]
                if sampled_point == False:# obstacle
                    self.built_map[y, x] = 0
                    # ddraw the obstacle
                    pygame.draw.circle(self.screen, color= (255, 0, 0), center=(x*self.grid_size, y*self.grid_size), radius=self.grid_size//2)
                    # add obstacle to the the list of obstacles if super class is set up 
                    try:
                        self.obstacle_map[y, x] = 1
                    except:
                        pass

                    break
                if r == max(ray_cast_samples):# frontier
                    if self.built_map[y, x] == 1:
                        break
                    self.built_map[y, x] = 2
                    pygame.draw.circle(self.screen, color=(251, 233, 89), center=(x*self.grid_size, y*self.grid_size), radius=self.grid_size//2)
                    break
                # free space
                self.built_map[y, x] = 1
                # pygame.draw.circle(self.screen, color= (0, 255, 0), center=(x, y), radius=self.grid_size//5)

            pygame.draw.line(self.screen, color= (255, 0, 0), 
                             start_pos=(self.grid_position[0]*self.grid_size, self.grid_position[1]*self.grid_size),
                             end_pos=(x*self.grid_size, y*self.grid_size),
                                width=1)

    def update(self, draw=True):
        # Update the agent's position

        self.scan()
        self.move()
        # self.draw()
        if draw:
            self.draw()
        
        # trade goal with other agents
