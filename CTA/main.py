import random
import pygame
import numpy as np

import world
import agent

random.seed(0)

# Initialize pygame
pygame.init()
# Define the size of the screen
cur_world = world.World()
    # Generate the floor plan
cur_world.generate_floor_plan()
map = cur_world.get_grid()
n_bots = 10
bots = []
for i in range(n_bots):
    bots.append(agent.Agent(screen = cur_world.screen,
                            body_size= 3,
                            lidar_range=10,
                            empty_map =np.zeros((map.shape[0], map.shape[1])).astype(bool)))

# Display the floor plan on the screen
pygame.display.update()

# Wait for the user to close the window
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
