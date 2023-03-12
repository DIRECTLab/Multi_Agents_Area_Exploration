import numpy as np
import matplotlib.pyplot as plt

class LogPlot:
    def __init__(self,cfg, data):
        self.cfg = cfg
        map_fig = plt.figure(figsize=(20, 10))
        ax1 = plt.subplot2grid((3, 2), (0, 0), rowspan=3, colspan=1)
        plot_rows = len(data.keys())
        log_ax = [ax1]
        for i in range(plot_rows):
            ax = plt.subplot2grid((plot_rows, 2), (i, 1), rowspan=1)
            log_ax.append(ax)
        
        for i, data_key in enumerate(list(data.keys())[0:plot_rows]):
            log_ax[i+1].set_ylabel(f"{data_key.replace('_', ' ').title()}")

        self.map_fig = map_fig
        self.log_ax = log_ax
        self.plot_rows = plot_rows
        # return map_fig, log_ax, plot_rows


    def draw_bots(self, bots, draw_paths=False):
        for i, bot in enumerate(bots):
            self.log_ax[0].scatter(bot.grid_position_xy[0], bot.grid_position_xy[1],
                        color='b', s=self.cfg.GRID_THICKNESS*2, marker='s')
            self.log_ax[0].scatter(bot.goal_xy[0], bot.goal_xy[1],
                        color='k', s=self.cfg.GRID_THICKNESS*2, marker='s')

            self.log_ax[0].text(bot.grid_position_xy[0], bot.grid_position_xy[1],
                        s=f"{i}",color='r', fontsize=18)                
            
            self.log_ax[0].text(bot.goal_xy[0], bot.goal_xy[1],
                        s=f"{i}",color='w', fontsize=18)
            

            

            if draw_paths:
                # past_traversed_locations
                x = [item[0] for item in bot.past_traversed_locations]
                y = [item[1] for item in bot.past_traversed_locations]
                self.log_ax[0].plot(x,y, color='b', linestyle=':', linewidth=1, alpha=0.5)

            # plan
            x = [item[0] for item in bot.plan]
            y = [item[1] for item in bot.plan]
            self.log_ax[0].plot(x,y, color='g', linestyle='--', linewidth=3)


    def plot_map(self, mutual_map, bots, data, start=0, stop=None):
        if stop is None:
            stop = len(data[list(data.keys())[0]])
        self.log_ax[0].clear()
        self.log_ax[0].matshow(mutual_map)
        self.draw_bots(bots)

        for i, data_key in enumerate(list(data.keys())[0:self.plot_rows]):
            self.log_ax[i+1].scatter(range(start, stop), data[data_key][start:stop], color='b', marker='.')
        # self.map_fig.canvas.draw()
        # self.map_fig.canvas.flush_events()
