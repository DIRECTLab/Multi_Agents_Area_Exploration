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

# Create a 2 dimensional array. A two dimensional array is simply a list of lists.
grid = []
queue = []
path = []

class Box:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.start = False
        self.wall = False
        self.target = False
        self.queued = False
        self.visited = False
        self.neighbors = []
        self.prior = None
        
    def draw(self, win, color):
        pygame.draw.rect(win,
                         color,
                         [(MARGIN + CELL_WIDTH) * self.column + MARGIN,
                         (MARGIN + CELL_HEIGHT) * self.row + MARGIN,
                         CELL_WIDTH,
                         CELL_HEIGHT])
    
    def set_neighbors(self):
        # horizontal neighbors
        if self.row > 0:
            self.neighbors.append(grid[self.row-1][self.column])
        if self.row < COLUMNS - 1:
            self.neighbors.append(grid[self.row+1][self.column])
        # vertical neighbors
        if self.column > 0:
            self.neighbors.append(grid[self.row][self.column-1])
        if self.column < ROWS - 1:
            self.neighbors.append(grid[self.row][self.column+1])


# create grid
for row in range(ROWS):
    # Add an empty array that will hold each cell in this row
    grid.append([])
    for column in range(COLUMNS):
        grid[row].append(Box(row,column))  # Append a cell

# set neighbors for all individual cells
for i in range(COLUMNS):
    for j in range(ROWS):
        grid[i][j].set_neighbors()

# Set row 0, column 0 as a start position.
start_box = grid[0][0] 
start_box.start = True
# start_box is the first visited box, and queue will be started appending from that cell
start_box.visited = True
queue.append(start_box)

target_box = grid[5][5]
target_box.target = True
target_box_set = True


# Set title of screen
pygame.display.set_caption("Auction Dijkstra Algorithm")


def main():
    begin_search = False
    # target_box_set = True
    searching = True
    # target_box = True
    
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
            if event.type == pygame.KEYDOWN and target_box_set:
                begin_search = True
        
        if begin_search:
            if len(queue) > 0 and searching:
                current_box = queue.pop(0)
                current_box.visited = True
                if current_box == target_box:
                    searching = False
                    while current_box.prior != start_box:
                        path.append(current_box.prior)
                        current_box = current_box.prior
                else:
                    for neighbor in current_box.neighbors:
                        if not neighbor.queued and not neighbor.wall:
                            neighbor.queued = True
                            neighbor.prior = current_box
                            queue.append(neighbor)
            else:
                if searching:
                    Tk().wm_withdraw()
                    messagebox.showinfo("No solution", "There is no solution!")
                    searching = False

        # Set the screen background
        screen.fill(COLOR_BLACK)

        # Draw the grid
        for row in range(ROWS):
            for column in range(COLUMNS):
                box = grid[row][column]
                box.draw(screen, COLOR_GRAY)

                if box.queued:
                    box.draw(screen, (200,0,0))
                if box.visited:
                    box.draw(screen, (0,200,0))
                if box in path:
                    box.draw(screen, (0,0,200))
                
                
                if box.start:
                    box.draw(screen, COLOR_CYAN)
                if box.wall:
                    box.draw(screen, COLOR_WALL_GRAY)
                if box.target:
                    box.draw(screen, COLOR_TARGET)

        
        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

main()
