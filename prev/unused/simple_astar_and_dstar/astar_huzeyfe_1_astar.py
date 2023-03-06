import pygame
import time
import math
import random

COLUMNS = 30
ROWS = 30
MARGIN = 3
CELL_WIDTH = 10
CELL_HEIGHT = 10
WINDOW_WIDTH = COLUMNS * (CELL_WIDTH + MARGIN) + MARGIN
WINDOW_HEIGHT = ROWS * (CELL_HEIGHT + MARGIN) + MARGIN

WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Basic Grid")
FPS = 60

BLACK = (0,0,0)
DARK_GRAY = (50,50,50)
GREEN = (0,255,0)
RED = (255,0,0)
BROWN = (102,51,0)
CYAN = (0, 255, 255)
PINK = (255, 0, 255)
YELLOW = (255, 255, 0)

# OPEN //the set of nodes to be evaluated
OPEN = []
# CLOSED //the set of nodes already evaluated
CLOSED = []
PATHTOFOLLOW = []

sleepTime = 0.001
# sleepTime = 1
startNode = None
endNode = None

class Node:
    def __init__(self,surface,x,y):
        self.surface = surface
        self.x = x
        self.y = y
        self.state = 0
        self.g_cost = 0
        self.h_cost = 0
        self.f_cost = 0
        self.previous = None
        
    def draw(self):
        state_of_cell = self.state
        match state_of_cell:
            case 0:     # EMPTY state
                pygame.draw.rect(self.surface, DARK_GRAY, [(MARGIN + CELL_WIDTH) * self.y + MARGIN, (MARGIN + CELL_HEIGHT) * self.x + MARGIN, CELL_WIDTH, CELL_HEIGHT])
            case 1:     # start
                pygame.draw.rect(self.surface, CYAN, [(MARGIN + CELL_WIDTH) * self.y + MARGIN, (MARGIN + CELL_HEIGHT) * self.x + MARGIN, CELL_WIDTH, CELL_HEIGHT])
            case 2:     # end
                pygame.draw.rect(self.surface, PINK, [(MARGIN + CELL_WIDTH) * self.y + MARGIN, (MARGIN + CELL_HEIGHT) * self.x + MARGIN, CELL_WIDTH, CELL_HEIGHT])
            case 3:     # wall
                pygame.draw.rect(self.surface, BROWN, [(MARGIN + CELL_WIDTH) * self.y + MARGIN, (MARGIN + CELL_HEIGHT) * self.x + MARGIN, CELL_WIDTH, CELL_HEIGHT])
            case 4:     # OPEN
                pygame.draw.rect(self.surface, GREEN, [(MARGIN + CELL_WIDTH) * self.y + MARGIN, (MARGIN + CELL_HEIGHT) * self.x + MARGIN, CELL_WIDTH, CELL_HEIGHT])
            case 5:     # CLOSED
                pygame.draw.rect(self.surface, RED, [(MARGIN + CELL_WIDTH) * self.y + MARGIN, (MARGIN + CELL_HEIGHT) * self.x + MARGIN, CELL_WIDTH, CELL_HEIGHT])
            case 6:     # PATH state
                pygame.draw.rect(self.surface, YELLOW, [(MARGIN + CELL_WIDTH) * self.y + MARGIN, (MARGIN + CELL_HEIGHT) * self.x + MARGIN, CELL_WIDTH, CELL_HEIGHT])
            case _:
                print("DEFAULT VALUE. DOES IT EVEN COME HERE?")
        
def createGrid():
    grid = []
    for i in range(ROWS):
        row = []
        for j in range(COLUMNS):
            col = Node(WINDOW,i,j)
            row.append(col)
        grid.append(row)
    return grid
grid = createGrid()

def main():
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                checkKeyboardEvent(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                checkMouseEvent(event)
        # randomly_generate_start_and_goal()
        draw_all()
        keys = pygame.key.get_pressed()
        if pygame.mouse.get_pressed()[1] and keys[pygame.K_LCTRL]:
            drawWalls()
    pygame.quit()

# def randomly_generate_start_and_goal():
#     global grid, startNode, endNode
#     row_s = random.randint(0, ROWS-1)
#     column_s = random.randint(0, COLUMNS-1)
#     if startNode == None:
#         if grid[row_s][column_s].state == 0:
#             grid[row_s][column_s].state = 1
#             startNode = grid[row_s][column_s]
#     row_g = random.randint(0, ROWS-1)
#     column_g = random.randint(0, COLUMNS-1)
#     if endNode == None and (row_g,column_g) != (row_s,column_s):
#         if grid[row_g][column_g].state == 0:
#             grid[row_g][column_g].state = 2
#             endNode = grid[row_g][column_g]

def checkMouseEvent(event):
    global grid, startNode, endNode
    mouse_pos = pygame.mouse.get_pos()
    row = mouse_pos[1] // (CELL_HEIGHT + MARGIN)
    column = mouse_pos[0] // (CELL_WIDTH + MARGIN)
    if event.button == 1: #left click
        if startNode == None:
            if grid[row][column].state == 0:
                grid[row][column].state = 1
                startNode = grid[row][column]
        else:
            if grid[row][column].state == 1:
                grid[row][column].state = 0
                startNode = None
    elif event.button == 3: # right click
        if endNode == None:
            if grid[row][column].state == 0:
                grid[row][column].state = 2
                endNode = grid[row][column]
        else:
            if grid[row][column].state == 2:
                grid[row][column].state = 0
                endNode = None
    elif event.button == 2: # middle click
        if grid[row][column].state == 0:
            grid[row][column].state = 3
        elif grid[row][column].state == 3:
            grid[row][column].state = 0

def checkKeyboardEvent(event):
    global OPEN, CLOSED, PATHTOFOLLOW, grid, startNode, endNode
    if event.key == pygame.K_r:
        print("reset the info")
        OPEN = []
        CLOSED = []
        PATHTOFOLLOW = []
        startNode = None
        endNode = None
        for x in range(ROWS):
            for y in range(COLUMNS):
                grid[x][y].state = 0
                grid[x][y].g_cost = 0
                grid[x][y].h_cost = 0
                grid[x][y].f_cost = 0
                grid[x][y].previous = None
    if event.key == pygame.K_4:
        AStar(4)
    elif event.key == pygame.K_8:
        AStar(8)

def AStar(neighbors):
    global OPEN, CLOSED, PATHTOFOLLOW, startNode, endNode
    if(startNode == None or endNode == None):
        return
    # add the start node to OPEN
    OPEN.append(startNode)
    while OPEN != []:
        time.sleep(sleepTime)
        draw_all()
        lowestFCostIndex = 0
        for i,x in enumerate(OPEN):
            if x.f_cost < OPEN[lowestFCostIndex].f_cost:
                lowestFCostIndex = i

        # current = node in OPEN with the lowest f_cost
        current = OPEN[lowestFCostIndex]
        # remove current from OPEN
        OPEN.remove(current)
        # add current to CLOSED
        CLOSED.append(current)

        # if current is the target node // path has been found
            # return
        if current == endNode:
            temp = current
            if temp.state != 1:
                temp.state = 6
            PATHTOFOLLOW.append(temp)
            while temp.previous:
                draw_all()
                time.sleep(sleepTime)
                if temp.previous.state != 1:
                    temp.previous.state = 6
                PATHTOFOLLOW.append(temp.previous)
                temp = temp.previous
            return
        
        # get the start node and change its state to CLOSED
        if current.state != 1:
            current.state = 5
        
        if neighbors == 4:
            currentNeighbours = checkNeighbours4(current.x,current.y)
        elif neighbors == 8:
            currentNeighbours = checkNeighbours8(current.x,current.y)
        
        # for each neighbor of the current node    
        for neighbour in currentNeighbours:
            # if neighbor is in closed
                # skip to the next neighbor
            if neighbour in CLOSED:
                continue

            # if the neighbor is a diagonal one, then  (g = current_g + 1.4)
            if current.x != neighbour.x and current.y != neighbour.y:
                tentGScore = current.g_cost + math.sqrt(2)
            # else the neighbor is a horizontal or vertical one. then (g = current_g + 1)
            else:
                tentGScore = current.g_cost + 1
            
            # if neighbor is not in OPEN
                # add neighbor to OPEN
            if neighbour not in OPEN:
                OPEN.append(neighbour)
                if neighbour.state != 1:
                    neighbour.state = 4
            
            elif tentGScore >= neighbour.g_cost:
                continue

            # set parent of neighbor to current
            neighbour.previous = current
            # set f_cost of neighbor
            neighbour.g_cost = tentGScore
            neighbour.h_cost = generateHeuristic(neighbour,endNode)
            neighbour.f_cost = neighbour.g_cost + neighbour.h_cost
            # print("for neighbor", neighbour.x, neighbour.y, ":", neighbour.f_cost)

def generateHeuristic(neigh,end):
    neighborPos = pygame.math.Vector2(neigh.x,neigh.y)
    endPos = pygame.math.Vector2(end.x,end.y)
    dist = neighborPos.distance_to(endPos)
    return dist

def checkNeighbours8(x, y):
    global grid
    neighbourCount = []
    for i in range(-1,2):
        for j in range(-1,2):
            col = x+i
            row = y+j
            if (col > -1 and col < COLUMNS) and (row > -1 and row < ROWS):
                if grid[col][row].state != 3:
                    neighbourCount.append(grid[col][row])
    return neighbourCount

def checkNeighbours4(x, y):
    global grid
    neighbourCount = []
    if x < COLUMNS -1 and grid[x+1][y].state != 3:
        neighbourCount.append(grid[x+1][y])
    if x > 0 and grid[x-1][y].state != 3:
        neighbourCount.append(grid[x-1][y])
    if y < ROWS -1 and grid[x][y+1].state != 3:
        neighbourCount.append(grid[x][y+1])
    if y > 0 and grid[x][y-1].state != 3:
        neighbourCount.append(grid[x][y-1])
    return neighbourCount

def drawWalls():
    global grid
    mouse_pos = pygame.mouse.get_pos()
    row = mouse_pos[1] // (CELL_HEIGHT + MARGIN)
    column = mouse_pos[0] // (CELL_WIDTH + MARGIN)
    if grid[row][column].state == 0 and row < ROWS and column < COLUMNS:
        grid[row][column].state = 3

def draw_all():
    draw_window()
    draw_board()
    update_display()

def draw_window(): 
    WINDOW.fill(BLACK)

def draw_board():
    for x in range(ROWS):
        for y in range(COLUMNS):
            grid[x][y].draw()

def update_display():
    pygame.display.update()

if __name__ == "__main__":
    main()