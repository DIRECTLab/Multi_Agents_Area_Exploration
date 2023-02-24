import random
import pygame
import numpy as np
import matplotlib.pyplot as plt
import threading

import src.world as world
import src.agent as agent

seed = 10
random.seed(seed)
np.random.seed(seed)

# Initialize pygame
pygame.init()
# Define the size of the screen
cur_world = world.World()
    # Generate the floor plan
map = cur_world.generate_floor_plan()
# cur_world.get_map(show_grid=True)
# map_fig, map_ax = plt.subplots(1, 1, figsize=(10, 10))
# map_ax.matshow(map)

# get current screen
map_screen = cur_world.screen.copy()
n_bots = 1
row = int(np.sqrt(n_bots))
col = int(np.ceil(n_bots/row))
bot_fig, bot_ax = plt.subplots(row, col, figsize=(10, 10))
if n_bots == 1:
    bot_ax = [bot_ax]
else:
    bot_ax = bot_ax.flatten()
plt.ion
bots = []
for i in range(n_bots):
    bots.append(agent.Agent(id= i,body_size= 3,
                            grid_size= world.GRID_THICKNESS,
                            lidar_range=map.shape[0]//3,
                            full_map = map,
                            position=(np.random.randint(0, map.shape[0]), 
                                      np.random.randint(0, map.shape[0])),
                            ax = bot_ax[i],screen=cur_world.screen))
    
    bot_ax[i].set_title(f"Bot {i}")
    bot_ax[i].matshow(bots[i].built_map)
# Display the floor plan on the screen
pygame.display.update()



useTheads = False
FPS = 160
clock = pygame.time.Clock()

cur_map = np.zeros((map.shape[0], map.shape[1])).astype(int)

# Wait for the user to close the window
frame_count = 0
while True:

    if useTheads:
        theads = []
        for bot in bots:
            # place each bot in a different thread
            t = threading.Thread(target=bot.update, args=(frame_count%10==0))
            t.start()
            theads.append(t)
            # take the and of the maps

            # cur_map = np.logical_and(cur_map, bot.built_map)
            cur_map *= bot.built_map
            cur_map += bot.built_map

                
        for i, (t, bot)  in enumerate(zip(theads,bots)):
            t.join()


    else:
        for i, bot in enumerate(bots):
            bot.update() #(draw=frame_count%10==0)
            cur_map *= bot.built_map
            cur_map += bot.built_map
            # ax[i].clear()
            # bot_ax[i].matshow(bot.built_map)
        


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

    # set the frame rate
    clock.tick(FPS)
    # print the frame rate
    print("clock.get_fps()",clock.get_fps(), end='\r')

    pygame.display.update()
    # clear the screen
    cur_world.screen.fill((0, 0, 0))
    # update the scrren
    cur_world.screen.blit(map_screen, (0, 0))
    
    # update the map but continue 
    # wait to update plt at FPS of 10
    if frame_count % 10 == 0:
        plt.pause(0.0001)
        plt.draw()


    frame_count += 1
