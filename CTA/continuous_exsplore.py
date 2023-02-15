
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)

# pip install python-maze-generator
from python_maze_generator import multithreaded_maze
import cv2

import random
import time 
# set seed
random.seed(0)

UNKNOWN = np.array([100, 100, 100], dtype=np.uint8)
FRONTIER = np.array([100, 100, 200], dtype=np.uint8)
KNOW = np.array([255, 255, 255], dtype=np.uint8)
OBSTACLE = np.array([0, 0, 0], dtype=np.uint8)


# We will create a random maze of size n x n
def create_maze(n,it,thre, scaleUP=10):
    # create a maze
    maze = multithreaded_maze.generate_mazes(n,n,it,thre)
    # convert PIL.Image.Image image mode=RGB size=234x234 to cv2 image
    maze.draw(solved=False, show=False)
    img = maze.image
    img = np.array(img.convert('1'))
    # scale up the image using np
    img = np.repeat(np.repeat(img, scaleUP, axis=0), scaleUP, axis=1)

    solution_path =[]
    solution_path_scaled = []
    scale_shit = img.shape[0]/len(maze.m)
    img12 = np.zeros(np.array(maze.m).shape, 3, dtype=np.uint8)
    img12.fill(255)
    # any location with maze.filled_wall
    img12 = np.where(maze.m == maze.filled_wall, OBSTACLE, img12)

    # Draw scaled up path 
    for i,row in enumerate(maze.m[:]):
        for j,col_item in enumerate(row):
            print(col_item, end=' ')
            if col_item == maze.solved_path:
                solution_path.append([i,j])
                solution_path_scaled.append([i*scale_shit,j*scale_shit])
                continue
            if i == 0 or i == len(maze.m)-1 or j == 0 or j == len(maze.m[0])-1:
                continue
            if col_item == maze.open_wall:
                # if above and below is a solved_path, then add to solution_path
                if maze.m[i-1][j] == maze.solved_path and maze.m[i+1][j] == maze.solved_path:
                    solution_path.append([i,j])
                    solution_path_scaled.append([i*scale_shit,j*scale_shit])
                    continue
                # if left and right is a solved_path, then add to solution_path
                if maze.m[i][j-1] == maze.solved_path and maze.m[i][j+1] == maze.solved_path:
                    solution_path.append([i,j])
                    solution_path_scaled.append([i*scale_shit,j*scale_shit])
                    continue
        print()

    return maze, img, solution_path, solution_path_scaled, scale_shit


class Agent:
    def __init__(self, img, startPose_rc, ax, grid_width, lidarRange):
        self.org_img = img.copy()
        self.pose_rc = startPose_rc
        
        # lidar range
        self.world_ax = ax[0]
        self.agent_map_ax = ax[1]

        self._body_size =int(grid_width)

        self.lidarRange = lidarRange
        self.lidar_sweep_res = np.arctan2(self._body_size, self.lidarRange)%np.pi
        self.lidar_step_res = self._body_size
        self.lidar_points = []

        # truncated occupancy grid integers
        self.ocupency_grid = np.zeros((img.shape[0]//self._body_size, img.shape[1]//self._body_size,3)).astype(np.uint8) +100
        self.ocu_pose_rc = [int(self.pose_rc[0]//self._body_size), int(self.pose_rc[1]//self._body_size)]

        self.drawSelf()

    def draw_fresh_map(self, new_img=None):
        # if a new image is provided, then draw the new image
        if new_img is not None:
            self.org_img = new_img.copy()
            self.world_ax.imshow(new_img, cmap=plt.gray())
        else:
            self.world_ax.imshow(self.org_img, cmap=plt.gray())
            # draw gid lines at _body_size
            
            self.world_ax.xaxis.set_major_locator(MultipleLocator(self._body_size*5))
            self.world_ax.yaxis.set_major_locator(MultipleLocator(self._body_size*5))
            self.world_ax.xaxis.set_minor_locator(AutoMinorLocator(self._body_size))
            self.world_ax.yaxis.set_minor_locator(AutoMinorLocator(self._body_size))
            self.world_ax.grid(which='major', color='#CCCCCC', linestyle='--')
            self.world_ax.grid(which='minor', color='#CCCCCC', linestyle=':')
            # move the grid under the points
            self.world_ax.set_axisbelow(True)


    def drawSelf(self):
        # draw an orange circle
        self.draw_fresh_map()

        self.drawLidar_angle()
        # self.drawLidar_grid()
        # self.world_ax.add_patch(plt.Circle((self.pose_rc[1], self.pose_rc[0]), self._body_size, color='green'))
        # self.agent_map_ax.add_patch(plt.Circle((self.pose_rc[1], self.pose_rc[0]), self._body_size, color='green'))
        
    
    def drawLidar_angle(self):

        # draw lidar
        self.world_ax.add_patch(plt.Circle((self.pose_rc[1], self.pose_rc[0]), self.lidarRange, color='blue', fill=False))
        # draw lidar points
        # sample the map to get lidar points
        # sweep the lidar 360 degrees and 
        for i, angle in enumerate(np.arange(0, 2*np.pi, self.lidar_sweep_res)):


            ray_cast_samples = np.arange(0,self.lidarRange, self.lidar_step_res)
            for j, r in enumerate(ray_cast_samples):
                # self.world_ax.add_patch(plt.Circle((self.pose_rc[1], self.pose_rc[0]), r, color='pink', fill=False))

                # get the point
                x = self.pose_rc[1] + r*np.cos(angle)
                y = self.pose_rc[0] + r*np.sin(angle)
                line = np.array([self.pose_rc[1], self.pose_rc[0], x, y])
                y_ocu, x_ocu = [int(y)//self._body_size-1,int(x)//self._body_size-1]
                if x < 0 or x >= img.shape[1] or y < 0 or y >= img.shape[0]:
                    break
                sampled_point= self.org_img[int(y), int(x)]
                smapled_point_ocu = self.ocupency_grid[y_ocu, x_ocu]
                if sampled_point == 0:# obstacle
                    self.world_ax.add_patch(plt.Circle((x, y), self._body_size/2, color='red'))
                    self.lidar_points.append([x,y])
                    self.ocupency_grid[y_ocu, x_ocu] = OBSTACLE
                    break
                if r == self.lidarRange-1:# frontier
                    self.world_ax.add_patch(plt.Circle((x, y), self._body_size/2, color='pink'))
                    self.lidar_points.append([x,y])
                    self.ocupency_grid[y_ocu, x_ocu] = FRONTIER
                    break
                if sampled_point == 255:# free space
                    self.world_ax.add_patch(plt.Circle((x, y), self._body_size/2, color='green'))
                    self.lidar_points.append([x,y])
                    self.ocupency_grid[y_ocu, x_ocu] = KNOW
                    break



        # draw ocupency grid color
        # cover to rgb image
        # rgb_img = cv2.cvtColor(self.ocupency_grid, cv2.COLOR_BGR2RGB)
        rgb_img = cv2.cvtColor(self.ocupency_grid, cv2.COLOR_RGB2BGR)
        
        self.agent_map_ax.imshow(rgb_img)
        return "done"


    def drawLidar_grid(self):

        
        # draw lidar
        self.world_ax.add_patch(plt.Circle((self.pose_rc[1], self.pose_rc[0]), self.lidarRange, color='blue', fill=False))

        # Spiraling Square lidar around the current pose at increments of the grid size
        for i in range(1, int(self.lidarRange),int( self.lidar_step_res)):
            # draw a square
            self.world_ax.add_patch(plt.Rectangle((self.pose_rc[1]-i, self.pose_rc[0]-i), 2*i, 2*i, color='red', fill=False))
            # sample the rectangle and draw the lidar points
            for j in range(1, 2*i +1, int(self.lidar_step_res)):
                # sample the top and bottom
                # sample the left and right
                for x,y in [(self.pose_rc[1]-i+j, self.pose_rc[0]-i), 
                            (self.pose_rc[1]-i+j, self.pose_rc[0]+i), 
                            (self.pose_rc[1]-i, self.pose_rc[0]-i+j), 
                            (self.pose_rc[1]+i, self.pose_rc[0]-i+j)]:
                    # check if the point is in the map
                    if x < 0 or x > img.shape[1] or y < 0 or y > img.shape[0]:
                        continue
                    ocu_x, ocu_y = [int(x)//self._body_size-1,int(y)//self._body_size-1]
                    if self.ocupency_grid[ocu_y,ocu_x].all() == OBSTACLE.all():
                        continue
                    if img[int(y),int(x)] == 0:
                        # draw the point
                        self.lidar_points.append([y,x])
                        # draw on agent map
                        self.world_ax.scatter(x, y, color='r', s=10)
                        # update the ocupency grid
                        # self.ocupency_grid[int(y),int(x)] = 0
                        self.ocupency_grid[ocu_y,ocu_x] = OBSTACLE
                        continue
                    if self.ocupency_grid[ocu_y,ocu_x].all() != UNKNOWN.all():
                        # pass
                        self.ocupency_grid[ocu_y,ocu_x] = KNOW
                        continue
                    self.ocupency_grid[ocu_y,ocu_x] = KNOW
                    self.world_ax.scatter(x, y, color='g', s=10)



        rgb_img = cv2.cvtColor(self.ocupency_grid, cv2.COLOR_RGB2BGR)
        
        self.agent_map_ax.imshow(rgb_img)
        return "done"
    
    def move(self):
        action = np.random.randint(-1,1,2)
        # action = [-1,-1]
        # check if the action is valid
        if self.ocu_pose_rc[0] + action[0] < 0 or \
            self.ocu_pose_rc[0] + action[0] > self.ocupency_grid.shape[0] or \
            self.ocu_pose_rc[1] + action[1] < 0 or \
            self.ocu_pose_rc[1] + action[1] > self.ocupency_grid.shape[1]:
            print("invalid action")
            return
        # check collision
        if self.ocupency_grid[self.ocu_pose_rc[0] + action[0], self.ocu_pose_rc[1] + action[1]].all() == OBSTACLE.all():
            print("collision")
            return self.move()
        else:
            # action is a tuple of (x,y)
            # move the agent
            self.ocu_pose_rc = [self.ocu_pose_rc[0] + action[0], self.ocu_pose_rc[1] + action[1]]
            self.pose_rc = [self.pose_rc[0] + action[0]*self._body_size, self.pose_rc[1] + action[1]*self._body_size]

        # draw the agent
        self.lidar_points = []
        # clears the entire current figure with all its axes
        self.world_ax.clear()
        self.agent_map_ax.clear()
        self.drawSelf()
        # return the lidar points
        return self.lidar_points


if __name__ == '__main__':
    n = 2#10
    maze, img, solution_path, solution_path_scaled, grid_width = create_maze(n,it = 10, thre = 4, scaleUP=1)


    fig, ax = plt.subplots(1,2,figsize=(10, 5))
    # ax flip y axis
    ax[1].invert_yaxis()
    # make the ax ready for image plotting
    ax[0].xaxis.tick_top()
    ax[1].xaxis.tick_top()


    # add a title
    ax[0].set_title('World')
    ax[1].set_title('Agent View')

    # bot1 = Agent(img, solution_path_scaled[0], ax, lidar_sample=100, lidarRange=2*scale_shit)
    bot_liat = []
    bot_n =2
    for i in range(bot_n):
        random_pose = [grid_width*(len(maze.m)-1),grid_width*(len(maze.m)-1)]
        # random_pose = [random.randint(0, len(maze.m)-1),random.randint(0, len(maze.m)-1)]
        bot1 = Agent(img,\
                    random_pose,\
                    ax,\
                    grid_width= grid_width/2,\
                    lidarRange=grid_width/2 * 5)
        bot_liat.append(bot1)

    number_of_frames = 100

    for i in range(number_of_frames):
            bot_liat[0].move()
            # time.sleep(0.2)
            plt.show()



    def update_plot(n):
        for bot in bot_liat:
            bot.move()
        # sleep
        time.sleep(0.2)
    
    # ani = animation.FuncAnimation(fig, update_plot, frames=number_of_frames, repeat=False )

    plt.show()




