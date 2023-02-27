import random
import pygame
import numpy as np
import matplotlib.pyplot as plt
import threading
from multiprocessing.pool import ThreadPool

import psutil
from tqdm import tqdm

import src.world as world
import src.agent as agent
from src.config import *

seed = 10
random.seed(seed)
np.random.seed(seed)

if DRAW_SIM:
    # Initialize pygame
    pygame.init()
# Define the size of the screen
cur_world = world.World()
# Generate the floor plan
map = cur_world.generate_floor_plan()
map_screen = cur_world.screen.copy()
# cur_world.get_map(show_grid=True)


if LOG_PLOTS:
    # create a map figure
    map_fig = plt.figure(figsize=(20, 10))
    ax1 = plt.subplot2grid((3, 2), (0, 0), rowspan=3, colspan=1)
    rows = 4
    log_ax = [ax1]
    for i in range(rows):
        ax = plt.subplot2grid((rows, 2), (i, 1), rowspan=1)
        log_ax.append(ax)
    log_ax[0].set_title(f"Max Known Area {map.size}")
    log_ax[1].set_ylabel(f"Known Area")
    log_ax[2].set_ylabel(f"Update Time")
    log_ax[3].set_ylabel(f"Delta Time")
    log_ax[4].set_ylabel(f"Plan Length")

    # space out the subplots
    map_fig.tight_layout()
    # create a grid of subplots 
    log_ax[0].matshow(map)


n_bots = 7
if DRAW_SIM:
    row = int(np.sqrt(n_bots))
    col = int(np.ceil(n_bots/row))
    bot_fig, bot_ax = plt.subplots(row, col, )#figsize=(10, 10))

    if n_bots == 1:
        bot_ax = [bot_ax]
    else:
        bot_ax = bot_ax.flatten()
    plt.ion()
bots = []
for i in range(n_bots):
    bots.append(agent.Agent(
                            id = i,
                            body_size = 3,
                            grid_size = GRID_THICKNESS,
                            lidar_range = map.shape[0]//3,
                            full_map = map,
                            ax = bot_ax[i] if DRAW_SIM else None,
                            screen = cur_world.screen if DRAW_SIM else None,
                        )
                )
    if DRAW_SIM:
        bot_ax[i].set_title(f"Bot {i}")
        bot_ax[i].matshow(bots[i].agent_map)

if DRAW_SIM:        
    # Display the floor plan on the screen
    pygame.display.update()
    FPS = 10
    clock = pygame.time.Clock()




useTheads = False
mutual_map = - np.ones((map.shape[0], map.shape[1])).astype(int)

# Wait for the user to close the window
frame_count = 0
dist_list = []
update_time_list = []
plan_length_list = []

sim_start_time = psutil.Process().cpu_times().user

while True:
    if useTheads:
        theads = []
        path_length = 0
        start_time = psutil.Process().cpu_times().user
        # for bot in bots:
        #     # place each bot in a different thread
        #     t = threading.Thread(target=bot.update, args=(mutual_map,DRAW_SIM ))
        #     t.start()
        #     theads.append(t)
                
        pool = ThreadPool(processes=len(bots))
        for i, bot in enumerate(bots):
            # place each bot in a different thread
            t = pool.apply_async(bot.update, (mutual_map,DRAW_SIM ))
            theads.append(t)


        for i, (t, bot)  in enumerate(zip(theads,bots)):
            [length, dist] = t.get()
            path_length += length


        end_time = psutil.Process().cpu_times().user
        update_time_list.append(end_time - start_time)
        plan_length_list.append(path_length)
        dist_list.append(dist)


    else:
        path_length = 0
        # time the bot update
        start_time = psutil.Process().cpu_times().user
        for i, bot in enumerate(bots):
            bot.update(mutual_map, draw=DRAW_SIM)
            path_length += len(bot.plan)
        end_time = psutil.Process().cpu_times().user
        update_time_list.append(end_time - start_time)
        plan_length_list.append(path_length)



    if DRAW_SIM:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        clock.tick(FPS)
        # update the scrren
        pygame.display.update()
        cur_world.screen.blit(map_screen, (0, 0))
        print("clock.get_fps()",clock.get_fps(), end='\r')

    cur_known = np.sum(mutual_map != -1)
    if LOG_PLOTS:
        # set the frame rate

        # update the map and plt
        log_ax[0].clear()
        log_ax[0].set_title(f"Max Known Area {map.size}")
        log_ax[0].matshow(mutual_map)
        for i, bot in enumerate(bots):
            log_ax[0].text(bot.grid_position[0], bot.grid_position[1],
                           s=f"{i}",color='r')
            log_ax[0].text(bot.goal[0], bot.goal[1],
                           s=f"{i}",color='w')
            x = [item[0] for item in bot.plan]
            y = [item[1] for item in bot.plan]
            log_ax[0].plot(x,y, color='g')
            
        
        log_ax[1].scatter(frame_count, cur_known, color='r')
        log_ax[2].scatter(frame_count, update_time_list[-1], color='g')
        log_ax[3].scatter(frame_count, psutil.Process().cpu_times().user, color='b')
        log_ax[4].scatter(frame_count, plan_length_list[-1], color='y')

    if LOG_PLOTS or DRAW_SIM:
        # update the map but continue 
        # wait to update plt at FPS of 10
        if frame_count % 1 == 0:
            # map_ax.matshow(mutual_map)
            plt.pause(0.00001)
            plt.draw()
    
    frame_count += 1
    if cur_known == mutual_map.size:
        break



