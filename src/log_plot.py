import numpy as np
import matplotlib.pyplot as plt

class LogPlot:
    def __init__(self,cfg, data, split_plot=True, plot_rows=None):
        self.cfg = cfg
        map_fig = plt.figure(figsize=(9, 7))
        map_fig.set_facecolor('black')
        plt.style.use('dark_background')

        map_ax = plt.subplot2grid((1, 2), (0, 0), rowspan=1, colspan=1)
        ax2 = plt.subplot2grid((1, 2), (0, 1), rowspan=1, colspan=1)

        # map_ax = plt.subplot2grid((1, 3), (0, 0), rowspan=3, colspan=1)
        # ax2 = plt.subplot2grid((3, 3), (0, 1), rowspan=3, colspan=2)
        # 1/2 for the map, 1/2 for the plot

        if plot_rows is None:
            plot_rows = len(data.keys())
        else: 
            plot_rows = plot_rows
        self.ax_dict = {}
        self.color_dict = {}

        self.split_plot = split_plot

        for i, data_key in enumerate(list(data.keys())[0:plot_rows]):
            self.color_dict[data_key] = f"C{i*2}"
            if self.split_plot:
                self.ax_dict[data_key] = plt.subplot2grid((plot_rows, 2), (i, 1), rowspan=1, colspan=1, )
            else:
                # Plot all data on the same plot
                self.ax_dict[data_key] = ax2.twinx()
                # chare the x axis
                # self.ax_dict[data_key].get_shared_x_axes().join(ax2, self.ax_dict[data_key])
                # offset the y axis
                self.ax_dict[data_key].spines["right"].set_position(("axes", 1+0.1*i))
                # set the color of the ticks
                self.ax_dict[data_key].tick_params(axis='y', colors=self.color_dict[data_key])

            self.ax_dict[data_key].set_ylabel(f"{data_key.replace('_', ' ').title()} █",
                                            color=self.color_dict[data_key],
                                            rotation=70,
                                            labelpad=0)
            
            self.ax_dict[data_key].set_xlabel("Frames")

        self.map_fig = map_fig
        self.map_ax = map_ax
        self.plot_rows = plot_rows
        # return map_fig, map_ax, plot_rows


    def draw_bots(self, bots, draw_paths=False):
        for i, bot in enumerate(bots):
            self.map_ax.scatter(bot.grid_position_xy[0], bot.grid_position_xy[1],
                        color='b', s=self.cfg.GRID_THICKNESS*2, marker='s')
            self.map_ax.scatter(bot.goal_xy[0], bot.goal_xy[1],
                        color='k', s=self.cfg.GRID_THICKNESS*2, marker='s')

            self.map_ax.text(bot.grid_position_xy[0], bot.grid_position_xy[1],
                        s=f"{i}",color='r', fontsize=18)                
            
            self.map_ax.text(bot.goal_xy[0], bot.goal_xy[1],
                        s=f"{i}",color='w', fontsize=18)
            
            if draw_paths:
                # past_traversed_locations
                x = [item[0] for item in bot.past_traversed_locations]
                y = [item[1] for item in bot.past_traversed_locations]
                self.map_ax.plot(x,y, color='b', linestyle=':', linewidth=1, alpha=0.5)

            # plan
            x = [item[0] for item in bot.plan]
            y = [item[1] for item in bot.plan]
            self.map_ax.plot(x,y, color='g', linestyle='--', linewidth=3)


    def plot_map(self, mutual_map, bots, data, start=0, stop=None):
        if stop is None:
            stop = len(data[list(data.keys())[0]])
        self.map_ax.clear()
        self.map_ax.matshow(mutual_map)
        self.draw_bots(bots)

        for i, data_key in enumerate(list(data.keys())[0:self.plot_rows]):


            self.ax_dict[data_key].plot(range(start, stop),
                                    data[data_key][start:stop],
                                    label=data_key,
                                    color=self.color_dict[data_key],)

