import numpy as np
import heapq
import matplotlib.pyplot as plt
import sys
import psutil

# heuristic function for path scoring
def heuristic(a, b):
    # return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

# path finding function
def astar(array, start, end):

    neighbors = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
    close_set = set()
    came_from = {}
    gscore = {start:0}
    fscore = {start:heuristic(start, end)}
    oheap = []
    heapq.heappush(oheap, (fscore[start], start))
 

    loop_count = 0
    start_time = psutil.Process().cpu_times().user

    while oheap:
        current = heapq.heappop(oheap)[1]
        if current == end:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data
        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:                
                    if array[neighbor[0]][neighbor[1]] == 1:
                        continue
                else:
                    # array bound y walls
                    continue
            else:
                # array bound x walls
                continue
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue
            if  tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, end)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))
        loop_count += 1
    
    end_time = psutil.Process().cpu_times().user
    print("loop_count:",loop_count)
    print("time:", end_time - start_time)
    return False

def main():
    # map = np.ones((10, 10))
    # map[0:9, 1:2] = 0
    # start = (0,0)
    # end = (9,9)

    # map = np.array([
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 0, 0, 0, 0, 0, 1, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
    # start = (4, 7)
    # end = (1, 4)

    map = np.zeros((100, 100))
    map[70:80, 0:100] = 1
    start = (0, 0)
    end = (99, 99)


    route = astar(map, start, end)
    print(route)
    if route is not False:
        route = route + [start]
        route = route[::-1]
        print(route)
    else:
        print("PATH NOT FOUND")
        sys.exit()

    # plot the path
    # extract x and y coordinates from route list
    x_coords = []
    y_coords = []
    for i in (range(0,len(route))):
        x = route[i][0]
        y = route[i][1]
        x_coords.append(x)
        y_coords.append(y)
    # plot map and path
    fig, ax = plt.subplots(figsize=(10,10))
    ax.imshow(map, cmap='Greys')
    ax.scatter(start[1],start[0], marker = "*", color = "blue", s = 200)
    ax.scatter(end[1],end[0], marker = "*", color = "green", s = 200)
    ax.plot(y_coords,x_coords, color = "green")
    plt.show()

if __name__ == '__main__':
    main()