# from warnings import warn
# import heapq

# # https://gist.github.com/ryancollingwood/32446307e976a11a1185a5394d6657bc

# class Node:
#     """
#     A node class for A* Pathfinding
#     """

#     def __init__(self, parent=None, position=None):
#         self.parent = parent
#         self.position = position

#         self.g = 0
#         self.h = 0
#         self.f = 0

#     def __eq__(self, other):
#         return self.position == other.position
    
#     def __repr__(self):
#       return f"{self.position} - g: {self.g} h: {self.h} f: {self.f}"

#     # defining less than for purposes of heap queue
#     def __lt__(self, other):
#       return self.f < other.f
    
#     # defining greater than for purposes of heap queue
#     def __gt__(self, other):
#       return self.f > other.f

# def return_path(current_node):
#     path = []
#     current = current_node
#     while current is not None:
#         path.append(current.position)
#         current = current.parent
#     return path[::-1]  # Return reversed path




# def astar(maze, start, end, allow_diagonal_movement = False):
#     """
#     Returns a list of tuples as a path from the given start to the given end in the given maze
#     :param maze:
#     :param start:
#     :param end:
#     :return:
#     """

#     # Create start and end node
#     start_node = Node(None, start)
#     start_node.g = start_node.h = start_node.f = 0
#     end_node = Node(None, end)
#     end_node.g = end_node.h = end_node.f = 0

#     # Initialize both open and closed list
#     open_list = []
#     closed_list = []

#     # Heapify the open_list and Add the start node
#     heapq.heapify(open_list) 
#     heapq.heappush(open_list, start_node)

#     # Adding a stop condition
#     outer_iterations = 0
#     max_iterations = (len(maze[0]) * len(maze) // 2)

#     # what squares do we search
#     adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0),)
#     if allow_diagonal_movement:
#         adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1),)

#     # Loop until you find the end
#     while len(open_list) > 0:
#         outer_iterations += 1

#         if outer_iterations > max_iterations:
#           # if we hit this point return the path such as it is
#           # it will not contain the destination
#           warn("giving up on pathfinding too many iterations")
#           return return_path(current_node)       
        
#         # Get the current node
#         current_node = heapq.heappop(open_list)
#         closed_list.append(current_node)

#         # Found the goal
#         if current_node == end_node:
#             return return_path(current_node)

#         # Generate children
#         children = []
        
#         for new_position in adjacent_squares: # Adjacent squares

#             # Get node position
#             node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

#             # Make sure within range
#             if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
#                 continue

#             # Make sure walkable terrain
#             if maze[node_position[0]][node_position[1]] != 0:
#                 continue

#             # Create new node
#             new_node = Node(current_node, node_position)

#             # Append
#             children.append(new_node)

#         # Loop through children
#         for child in children:
#             # Child is on the closed list
#             if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
#                 continue

#             # Create the f, g, and h values
#             child.g = current_node.g + 1
#             child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
#             child.f = child.g + child.h

#             # Child is already in the open list
#             if len([open_node for open_node in open_list if child.position == open_node.position and child.g > open_node.g]) > 0:
#                 continue

#             # Add the child to the open list
#             heapq.heappush(open_list, child)

#     warn("Couldn't get a path to destination")
#     return None


# class Node:
#     def __init__(self, position, parent, g, h):
#         self.position = position
#         self.parent = parent
#         self.g = g  # cost to reach this node from the start node
#         self.h = h  # estimated cost to reach the end

#     def __lt__(self, other):
#         return self.g + self.h < other.g + other.h


import heapq
import matplotlib.pyplot as plt

import psutil


import heapq

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

def astar(map, start, end, allow_diagonal_movement=False, debug=False, ax=None):
    # convert start and end tuples from (x, y) to (row, col)
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
    start_time = 0
    if debug:
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
            if allow_diagonal_movement and i >= 4:
                # diagonal move
                successor_g = current_node.g + map[row+drow, col+dcol] * 1.414  # sqrt(2)
            else:
                # straight move
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
            
            if ax:
                # draw the explored nodes
                import numpy as np
                rand_color = np.random.rand(3)
                # ax.plot(col+dcol, row+drow, "x", color=rand_color, markersize=6)
                # draw rectangle
                ax.add_patch(plt.Rectangle((col+dcol-0.5, row+drow-0.5), 1, 1, color=rand_color, alpha=0.5))

                plt.pause(0.1)
                plt.draw()

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

    if debug:
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
    import numpy as np
    # map = np.array([
    #     [1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
    #     [1, 0, 1, 0, 1, 1, 1, 1, 0, 1],
    #     [1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    #     [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    #     [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    #     [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    #     [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    #     [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    #     [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],])

    # map = np.linspace(1, 100, 100).reshape(10, 10
    map = np.ones((100, 100))

    # draw a L
    # map[7:8, 2:8] = 0
    # map[2:8, 7:8] = 0

    map[70:80, 0:100] = 0
    map[2:8, 7:8] = 0

    
    start = (0, 0)
    end = (99, 99)
    fig,ax = plt.subplots()
    # plt.ion()
    path =None
    plt.imshow(map, cmap='Greys', origin='lower')
    path = astar(map, start, end, allow_diagonal_movement=True, debug=False, ax = ax)

    if path is not None:
        print("Found path:", path)
        print("Path length:", len(path))
    else:
        print("No path found")

    plt.plot(start[0], start[1], 'bs')
    plt.plot(end[0], end[1], 'gs')
        
    if path is not None:
        path = np.array(path)
        plt.plot(path[:, 0], path[:, 1], 'g-')

    plt.show()

if __name__ == '__main__':
    main()