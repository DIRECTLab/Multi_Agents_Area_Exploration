from tkinter import messagebox, Tk
import pygame
import sys


COLUMNS = 25
ROWS = 25
# This sets the margin between each cell
MARGIN = 5
# This sets the WIDTH and HEIGHT of each grid location
CELL_WIDTH = 20
CELL_HEIGHT = 20
# Set the HEIGHT and WIDTH of the screen
WINDOW_WIDTH = COLUMNS * (CELL_WIDTH + MARGIN) + MARGIN
WINDOW_HEIGHT = ROWS * (CELL_HEIGHT + MARGIN) + MARGIN
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
# Define some colors
COLOR_BLACK = (0,0,0)
COLOR_GRAY = (50,50,50)
COLOR_WALL_GRAY = (90,90,90)
COLOR_GREEN = (0,255,0)
COLOR_CYAN = (0,200,200)
COLOR_TARGET = (200,200,0)


class Box:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.start = False
        self.wall = False
        self.target = False
        
    def draw(self, win, color):
        pygame.draw.rect(win,
                            color,
                            [(MARGIN + CELL_WIDTH) * self.column + MARGIN,
                            (MARGIN + CELL_HEIGHT) * self.row + MARGIN,
                            CELL_WIDTH,
                            CELL_HEIGHT])


# Create a 2 dimensional array. A two dimensional array is simply a list of lists.
grid = []
for row in range(ROWS):
    # Add an empty array that will hold each cell in this row
    grid.append([])
    for column in range(COLUMNS):
        grid[row].append(Box(row,column))  # Append a cell

# Set row 0, column 0 as a start position.
start_box = grid[0][0] 
start_box.start = True

# Set title of screen
pygame.display.set_caption("Auction Dijkstra Algorithm")


def main():
    begin_search = False
    target_box_set = False
    
    # -------- Main Program Loop -----------
    while True:
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                pygame.quit()   # we are done so we exit this loop
                sys.exit()
            # set wall
            elif event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()    # User clicks the mouse. Get the position
                # Change the x/y screen coordinates to grid coordinates
                column = pos[0] // (CELL_WIDTH + MARGIN)
                row = pos[1] // (CELL_HEIGHT + MARGIN)
                if event.buttons[0]:
                    grid[row][column].wall = True
                    # print("Grid coordinates: ", row, column)
            # set target
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3 and not target_box_set:
                    pos = pygame.mouse.get_pos()    # User clicks the mouse. Get the position
                    # Change the x/y screen coordinates to grid coordinates
                    column = pos[0] // (CELL_WIDTH + MARGIN)
                    row = pos[1] // (CELL_HEIGHT + MARGIN)
                    # print("Grid coordinates: ", row, column)
                    target_box = grid[row][column]
                    target_box.target = True
                    target_box_set = True
            # start algorithm
            if event.type == pygame.KEYDOWN and target_box_set:
                begin_search = True

        # Set the screen background
        screen.fill(COLOR_BLACK)

        # Draw the grid
        for row in range(ROWS):
            for column in range(COLUMNS):
                box = grid[row][column]
                box.draw(screen, COLOR_GRAY)
                if box.start:
                    box.draw(screen, COLOR_CYAN)
                if box.wall:
                    box.draw(screen, COLOR_WALL_GRAY)
                if box.target:
                    box.draw(screen, COLOR_TARGET)

        
        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

main()
