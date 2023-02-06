
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
# pip install python-maze-generator
from python_maze_generator import multithreaded_maze
import cv2

import random
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
    def __init__(self, img, startPose, ax, lidar_sample=20, lidarRange =20):
        self.org_img = img.copy()
        self.pose_rc = startPose
        
        # lidar range
        self.world_ax = ax[0]
        self.agent_map_ax = ax[1]

        self._body_size = lidar_sample // 5

        self.lidar_sweep_res = lidar_sample
        self.lidarRange = lidarRange
        self.lidar_step_res = self._body_size//5
        self.lidar_points = []

        # truncated occupancy grid integers
        self.ocupency_grid = np.zeros((img.shape[0]//self._body_size, img.shape[1]//self._body_size,3)).astype(np.uint8) +100
        self.ocu_scale = self._body_size

        self.drawSelf()

    def draw_fresh_map(self, new_img=None):
        # if a new image is provided, then draw the new image
        if new_img is not None:
            self.org_img = new_img.copy()
            self.world_ax.imshow(new_img, cmap=plt.gray())
        else:
            self.world_ax.imshow(self.org_img, cmap=plt.gray())

    def drawSelf(self):
        # draw an orange circle
        self.draw_fresh_map()

        self.drawLidar()
        self.world_ax.add_patch(plt.Circle((self.pose_rc[1], self.pose_rc[0]), self._body_size, color='green'))
        # self.agent_map_ax.add_patch(plt.Circle((self.pose_rc[1], self.pose_rc[0]), self._body_size, color='green'))
        

    def drawLidar(self):

        
        # draw lidar
        self.world_ax.add_patch(plt.Circle((self.pose_rc[1], self.pose_rc[0]), self.lidarRange, color='blue', fill=False))
        # draw lidar points
        # sample the map to get lidar points
        # sweep the lidar 360 degrees and 
        for ray in np.arange(0,2*np.pi,2*np.pi/self.lidar_sweep_res):
            # ray trace to the 1st intersection
            # draw a line for this ray
            line = np.array([self.pose_rc[1], self.pose_rc[0], self.pose_rc[1] + self.lidarRange*np.cos(ray), self.pose_rc[0] + self.lidarRange*np.sin(ray)])
            self.world_ax.plot(line[[0,2]], line[[1,3]], color='blue', alpha=0.25)

            ray_cast_samples = np.arange(0,self.lidarRange, self.lidar_step_res)
            for i, r in enumerate(ray_cast_samples):
                self.world_ax.add_patch(plt.Circle((self.pose_rc[1], self.pose_rc[0]), r, color='pink', fill=False))

                # get the point
                x = self.pose_rc[1] + r*np.cos(ray)
                y = self.pose_rc[0] + r*np.sin(ray)
                y_ocu, x_ocu = [int(y)//self._body_size-1,int(x)//self._body_size-1]

                if self.ocupency_grid[y_ocu,x_ocu].all() == OBSTACLE.all():
                    break

                # check if the point is in the map
                if x < 0 or x > img.shape[1] or y < 0 or y > img.shape[0]:
                    break
                if img[int(y),int(x)] == 0:
                    # draw the point
                    self.lidar_points.append([y,x])
                    # draw on agent map
                    self.world_ax.scatter(x, y, color='r', s=10)
                    # update the ocupency grid
                    # self.ocupency_grid[int(y),int(x)] = 0
                    self.ocupency_grid[y_ocu,x_ocu] = OBSTACLE
                    break


                # if at the end of the ray, then add the end point
                if i >= len(ray_cast_samples)-2:
                    self.ocupency_grid[y_ocu,x_ocu] = FRONTIER
                    break
                elif self.ocupency_grid[y_ocu,x_ocu].all() != UNKNOWN.all():
                #     self.ocupency_grid[y_ocu,x_ocu] = KNOW
                #     break
                self.ocupency_grid[y_ocu,x_ocu] = KNOW

        # draw ocupency grid color
        # cover to rgb image
        # rgb_img = cv2.cvtColor(self.ocupency_grid, cv2.COLOR_BGR2RGB)
        rgb_img = cv2.cvtColor(self.ocupency_grid, cv2.COLOR_RGB2BGR)
        
        self.agent_map_ax.imshow(rgb_img)
        return "done"
    
    def move(self):
        # action = np.random.randint(-1,1,2)
        action = [-10,-10]
        # check if the action is valid
        if self.pose_rc[0] + action[0] < 0 or \
            self.pose_rc[0] + action[0] > img.shape[0] or \
            self.pose_rc[1] + action[1] < 0 or \
            self.pose_rc[1] + action[1] > img.shape[1]:
            print("invalid action")
            return
        # action is a tuple of (x,y)
        # move the agent
        self.pose_rc[0] += action[0]
        self.pose_rc[1] += action[1]
        # draw the agent
        self.lidar_points = []
        self.drawSelf()
        # return the lidar points
        return self.lidar_points

if __name__ == '__main__':
    n = 5
    maze, img, solution_path, solution_path_scaled, scale_shit = create_maze(n,it = 10, thre = 4, scaleUP=2)


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
    bot1 = Agent(img,\
                [scale_shit*(len(maze.m)-1),scale_shit*(len(maze.m)-1)],\
                ax,\
                lidar_sample=100, \
                lidarRange=2*scale_shit)

    # # take the average of the lidar points
    # for i in range(100):

    #     # move the bot  
    #     bot1.move()
    # plt.show()
    number_of_frames = 100



    def update_plot(n):
        bot1.move()

    ani = animation.FuncAnimation(fig, update_plot, frames=number_of_frames, repeat=False )
    plt.show()




