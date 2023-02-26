# Define the size of the walls
GRID_THICKNESS = 10

# Define the size of the screen
SCREEN_WIDTH = 100 * GRID_THICKNESS
SCREEN_HEIGHT = 100 * GRID_THICKNESS

# Define the colors to be used in the drawing
BACKGROUND_COLOR = (78, 157, 157)
WALL_COLOR = (80, 24, 99)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (251, 233, 89)
PINK = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TEAL = (0, 128, 128)



# Define the minimum and maximum sizes for the rooms
MIN_ROOM_SIZE = 10 * GRID_THICKNESS
MAX_ROOM_SIZE = 20 * GRID_THICKNESS


# Map location definitions
UNKNOWN = -1
KNOWN_WALL = 0
KNOWN_EMPTY = 1
FRONTIER = 2