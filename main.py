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

# seed = 10
# random.seed(seed)
# np.random.seed(seed)

def run_experiment():
    import os

    if DRAW_SIM:
        # Initialize pygame
        pygame.init()
    else:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    # Define the size of the screen
    cur_world = world.World()
    # Generate the floor plan
    map = cur_world.generate_floor_plan()
    map_screen = cur_world.screen.copy()
    # cur_world.get_map(show_grid=True)

    data= {
        'area_percent' : [],
        'update_time' : [],
        'delta_time' : [],
        'plan_length' : [],
        'replan_count' : [],
        'frame_count': [],
        'known_area' : [],
        }



    if LOG_PLOTS:
        # create a map figure
        map_fig = plt.figure(figsize=(20, 10))
        ax1 = plt.subplot2grid((3, 2), (0, 0), rowspan=3, colspan=1)
        plot_rows = 5
        log_ax = [ax1]
        for i in range(plot_rows):
            ax = plt.subplot2grid((plot_rows, 2), (i, 1), rowspan=1)
            log_ax.append(ax)
        log_ax[0].set_title(f"Max Known Area {map.size}")
        for i, data_key in enumerate(list(data.keys())[0:plot_rows]):
            log_ax[i+1].set_ylabel(f"{data_key.replace('_', ' ').title()}")


        # space out the subplots
        map_fig.tight_layout()
        # create a grid of subplots 
        log_ax[0].matshow(map)


    if DRAW_SIM:
        row = int(np.sqrt(N_BOTS))
        col = int(np.ceil(N_BOTS/row))
        bot_fig, bot_ax = plt.subplots(row, col, )#figsize=(10, 10))

        if N_BOTS == 1:
            bot_ax = [bot_ax]
        else:
            bot_ax = bot_ax.flatten()
        plt.ion()
    bots = []
    for i in range(N_BOTS):
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




    
    mutual_map = - np.ones((map.shape[0], map.shape[1])).astype(int)

    # Wait for the user to close the window
    frame_count = 0
    sim_start_time = psutil.Process().cpu_times().user
    while True:
        path_length = 0
        replan_count = 0
        if USE_THREADS:
            threads = []
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
                threads.append(t)


            for i, (t, bot)  in enumerate(zip(threads,bots)):
                [length, dist] = t.get()
                path_length += length
            end_time = psutil.Process().cpu_times().user



        else:
            # time the bot update
            start_time = psutil.Process().cpu_times().user
            for i, bot in enumerate(bots):
                bot.update(mutual_map, draw=DRAW_SIM)
                path_length += len(bot.plan)
                replan_count += bot.replan_count
            end_time = psutil.Process().cpu_times().user



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
        data['area_percent'].append(cur_known / mutual_map.size)
        data['update_time'].append(end_time - start_time)
        data['delta_time'].append( psutil.Process().cpu_times().user - sim_start_time)
        data['plan_length'].append(path_length)
        data['replan_count'].append(replan_count)
        data['frame_count'].append(frame_count)
        data['known_area'].append(cur_known)

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
                
            for i, data_key in enumerate(list(data.keys())[0:plot_rows]):
                log_ax[i+1].scatter(frame_count, data[data_key][-1], color='g')

        if LOG_PLOTS or DRAW_SIM:
            # update the map but continue 
            # wait to update plt at FPS of 10
            if frame_count % 3 == 0:
                # map_ax.matshow(mutual_map)
                plt.pause(0.00001)
                plt.draw()
        
        frame_count += 1
        if cur_known == mutual_map.size:
            break

    print("Done: Saving Data")
    import time
    import os
    import pandas as pd
    folder_date = time.strftime("%Y/%m/%d_%H:%M:%S")
    # create expeament folder
    os.makedirs(f"data/{folder_date}", exist_ok=True)

    if LOG_PLOTS:
        map_fig.savefig(f"data/{folder_date}/map_fig.png")

    if DRAW_SIM:
        # save the screen
        pygame.image.save(cur_world.screen, f"data/{folder_date}/screen.png")
        pygame.quit()

    # save the data
    df = pd.DataFrame(data)
    df.to_csv(f"data/{folder_date}/data.csv")
    print("Done")

def main():
    from tqdm import tqdm
    # import multiprocessing
    from multiprocessing import Process, Queue
    agent_ramges = np.arange(1,10)
    Process_list = []
    for i in range(10):
        print(i)
        run_experiment()
        # # run the simulation in a new process
        # p = Process(target=run_experiment, args=())
        # p.start()
        # Process_list.append(p)

    for p in Process_list:
        p.join()

if __name__ == "__main__":
    main()