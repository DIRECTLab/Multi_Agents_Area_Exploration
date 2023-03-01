import heapq
import matplotlib.pyplot as plt
import psutil
import heapq
import numpy as np

class Node:
    def __init__(self, position, parent=None, g=0, h=0):
        self.position = position
        self.parent = parent
        self.g = g
        self.h = h

    def f(self):
        return self.g + self.h

    def __lt__(self, other):
        return self.f() < other.f()

def astar(map, start, end):
    # print(start)
    # print(end)
    start = (start[1], start[0])
    end = (end[1], end[0])

    # create the start and end nodes
    start_node = Node(start)
    end_node = Node(end)

    # initialize the open list and the closed list
    open_list = []
    closed_list = set()

    # add the start node to the open list
    heapq.heappush(open_list, start_node)

    max_iterations = (len(map[0]) * len(map) // 2)
    loop_count = 0
    start_time = psutil.Process().cpu_times().user
    # loop until the open list is empty
    while open_list:
        # pop the node with the lowest f-value from the open list
        current_node = heapq.heappop(open_list)

        # check if we have reached the end node
        if current_node.position == end_node.position:
            # construct the path by following the parent pointers
            path = []
            node = current_node
            while node:
                # convert node position from (row, col) to (x, y)
                path.append((node.position[1], node.position[0]))
                # path.append((node.position[0], node.position[1]))
                node = node.parent
            # return the reversed path
            return path[::-1]

        # add the current node to the closed list
        closed_list.add(current_node.position)

        # generate the successors of the current node
        row, col = current_node.position
        for i, (drow, dcol) in enumerate(((0, 1), (0, -1), (1, 0), (-1, 0), (-1, -1), (1, 1), (-1, 1), (1, -1))):
            # check if the successor is out of bounds or an obstacle
            if not (0 <= row+drow < map.shape[0] and 0 <= col+dcol < map.shape[1]) or map[row+drow, col+dcol] == 0:
                continue

            # compute the cost to move to the successor
            
            successor_g = current_node.g + map[row+drow, col+dcol]

            #check if the successor is already in the open list
            for node in open_list:
                if node.position == (row+drow, col+dcol):
                    # update the existing node if the new path is better
                    if successor_g < node.g:
                        node.g = successor_g
                        node.parent = current_node
                    break


            # compute the heuristic value of the successor
            successor_h = heuristic((row+drow, col+dcol), end)

            # create the successor node
            successor_node = Node((row+drow, col+dcol), current_node, successor_g, successor_h)

            # check if the successor is already in the closed list
            if successor_node.position in closed_list:
                continue

            # check if the successor is already in the open list
            for node in open_list:
                if node.position == successor_node.position:
                    # update the existing node if the new path is better
                    if successor_node.g < node.g:
                        node.g = successor_node.g
                        node.parent = successor_node.parent
                        heapq.heapify(open_list)  # re-heapify the open list
                    break

            else:
                # add the successor to the open list
                heapq.heappush(open_list, successor_node)
        
        loop_count += 1
        # if loop_count > max_iterations:
        #     print("Exceeded max iterations")
        #     break

    end_time = psutil.Process().cpu_times().user
    print("loop_count:",loop_count)
    print("time:", end_time - start_time)
    # if we reach this point, there is no path from start to end
    return None

def heuristic(a, b):
    # # compute the Manhattan distance between a and b
    # return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # compute the Euclidean distance between a and b
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

def main():
    
    # map = np.ones((10, 10))
    # map[0:9, 1:2] = 0
    # start = (0,0)
    # end = (9,9)
    
    # map = np.array([
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 0, 0, 0, 0, 0, 1, 1],
    #     [1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
    # start = (7, 5)
    # end = (4, 8)

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

    map = np.ones((100, 100))
    map[70:80, 0:100] = 0
    start = (0, 0)
    end = (99, 99)

    fig,ax = plt.subplots()
    # plt.ion()
    path = None
    plt.imshow(map, cmap='Greys')
    path = astar(map, start, end)

    if path is not None:
        print("Found path:", path)
        print("Path length:", len(path))
        plt.scatter(start[0],start[1], marker = "*", color = "blue", s = 200)
        plt.scatter(end[0],end[1], marker = "*", color = "green", s = 200)
        # plt.scatter(start[1],start[0], marker = "*", color = "blue", s = 200)
        # plt.scatter(end[1],end[0], marker = "*", color = "green", s = 200)
        path = np.array(path)
        plt.plot(path[:, 0], path[:, 1], 'g-')
        plt.show()
    else:
        print("No path found")

if __name__ == '__main__':
    main()