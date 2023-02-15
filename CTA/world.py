# this will hold the world class

import pygame
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Define the size of the screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Define the colors to be used in the drawing
BACKGROUND_COLOR = (255, 255, 255)
WALL_COLOR = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


# Define the size of the walls
WALL_THICKNESS = 8

# Define the minimum and maximum sizes for the rooms
MIN_ROOM_SIZE = 50
MAX_ROOM_SIZE = 300




# Define a class to represent a rectangular room
class Room:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        # door is a list of positions to draw doors
        self.doors = []

class World:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((SCREEN_WIDTH+WALL_THICKNESS, SCREEN_HEIGHT+WALL_THICKNESS))
        self.screen.fill(BACKGROUND_COLOR)
        self.walls = []
        self.doors = []
        self.rooms = []
        self.room_count = 0


    # Define a function to draw a wall
    def draw_wall(self, x1, y1, x2, y2, thickness=WALL_THICKNESS, color= WALL_COLOR):
        # convert to integer
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), thickness)
        self.walls.append(pygame.Rect(x1, y1, x2 - x1, y2 - y1))

    def draw_door(self, x1, y1, x2, y2, thickness=WALL_THICKNESS, color= BACKGROUND_COLOR):
        # square door
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), thickness)
        self.doors.append(pygame.Rect(x1, y1, x2 - x1, y2 - y1))

    # Define a function to recursively split a rectangle into smaller rooms
    def split_rect(self, rect, min_size):
        rooms = []

        if rect.w < min_size * 2 or rect.h < min_size * 2:
            cur_room = Room(rect.x, rect.y, rect.w, rect.h)
            # add doors randomly to the sides of the room
            # the door is a square of WALL_THICKNESS
            cur_room.doors.append((rect.x, random.randint(rect.y, rect.y + rect.h - WALL_THICKNESS)))
            # add door on the top side
            cur_room.doors.append((random.randint(rect.x, rect.x + rect.w - WALL_THICKNESS), rect.y))
               
            return [cur_room]

        if rect.w > rect.h:
            split_pos = random.randint(rect.x + min_size, rect.x + rect.w - min_size)
            rooms += self.split_rect(pygame.Rect(rect.x, rect.y, split_pos - rect.x, rect.h), min_size)
            rooms += self.split_rect(pygame.Rect(split_pos, rect.y, rect.x + rect.w - split_pos, rect.h), min_size)
        else:
            split_pos = random.randint(rect.y + min_size, rect.y + rect.h - min_size)
            rooms += self.split_rect(pygame.Rect(rect.x, rect.y, rect.w, split_pos - rect.y), min_size)
            rooms += self.split_rect(pygame.Rect(rect.x, split_pos, rect.w, rect.y + rect.h - split_pos), min_size)

        return rooms

    # Define a function to generate a random floor plan
    def generate_floor_plan(self):
        # Generate the walls of the outer boundary of the floor plan
        pygame.draw.rect(self.screen, WALL_COLOR, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), WALL_THICKNESS)

        # Generate the rooms
        rooms = self.split_rect(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT ), MIN_ROOM_SIZE)

        # Draw the walls of the rooms
        for room in rooms:
            self.draw_wall(room.x, room.y, room.x + room.w, room.y)
            self.draw_wall(room.x + room.w, room.y, room.x + room.w, room.y + room.h)

            # draw the doors
            for door in room.doors:
                x, y = door
                # if vertical door
                if x == room.x:
                    self.draw_door(x, y, x, y + WALL_THICKNESS*2)
                else:
                    self.draw_door(x, y, x + WALL_THICKNESS*2, y )

    def draw_grid(self, color):
        # draw a thin grid 
        for x in range(0, SCREEN_WIDTH, 10):
            pygame.draw.line(self.screen, color, (x, 0), (x, SCREEN_HEIGHT))

        for y in range(0, SCREEN_HEIGHT, 10):
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

    def get_grid(self, show_grid=False):
        # show the floor plan in matplotlib
        fig, ax = plt.subplots()
        
        world_grid = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH)).astype(bool)
        world_grid.fill(True)
        
        for wall in self.walls:
            x, y = wall.x, wall.y
            w, h = wall.w, wall.h
            if w == 0:
                w = 1
            if h == 0:
                h = 1
            world_grid[y:y+h, x:x+w] = 0
        
        for door in self.doors:
            x, y = door.x, door.y
            w, h = door.w, door.h
            if w == 0:
                w = 1
            if h == 0:
                h = 1
            world_grid[y:y+h, x:x+w] = 1

        # draw border
        world_grid[0, :] = 0
        world_grid[-1, :] = 0
        world_grid[:, 0] = 0
        world_grid[:, -1] = 0

        ax.imshow(world_grid, cmap='gray')
        plt.show()
        return world_grid