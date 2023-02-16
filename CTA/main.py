import random
import pygame
import numpy as np

import world
import agent

seed = 42
random.seed(seed)
np.random.seed(seed)

# Initialize pygame
pygame.init()
# Define the size of the screen
cur_world = world.World()
    # Generate the floor plan
map = cur_world.generate_floor_plan()
# get current screen
map_screen = cur_world.screen.copy()
n_bots = 2
bots = []
for i in range(n_bots):
    bots.append(agent.Agent(body_size= 3,
                            grid_size= world.WALL_THICKNESS,
                            lidar_range=world.SCREEN_WIDTH//3,
                            full_map = map))

# Display the floor plan on the screen
pygame.display.update()

debug = True
if debug:
    test_bot = agent.Agent(body_size= 3,
                           grid_size= world.WALL_THICKNESS,
                           lidar_range=world.SCREEN_WIDTH//3,
                           full_map = map,
                            position=(50, 50))

    FPS = 60
    clock = pygame.time.Clock()

# Wait for the user to close the window
while True:

    cur_map = np.zeros((world.SCREEN_HEIGHT, world.SCREEN_WIDTH)).astype(int)
    for bot in bots:
        bot.update(map, cur_world.screen)
        cur_map += bot.built_map
            
    # assign the map screen to the current screen
    # cur_world.screen = map_screen.copy()
    if debug:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # arrow keys
            if event.type == pygame.KEYDOWN:
                # quit the game if q is pressed
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()

                if event.key == pygame.K_LEFT:
                    test_bot.dx += -0.1
                if event.key == pygame.K_RIGHT:
                    test_bot.dx += 0.1
                if event.key == pygame.K_UP:
                    test_bot.dy += -0.1
                if event.key == pygame.K_DOWN:
                    test_bot.dy += 0.1

                # space bar
                if event.key == pygame.K_SPACE:
                    test_bot.dy = 0
                    test_bot.dx = 0

        test_bot.update(map, cur_world.screen)
                # set the frame rate
        clock.tick(FPS)
        # print the frame rate
        print("clock.get_fps()",clock.get_fps(), end='\r')

    pygame.display.update()
    # clear the screen
    cur_world.screen.fill((0, 0, 0))
    # update the scrren
    cur_world.screen.blit(map_screen, (0, 0))



