class Config:
    def __init__(self):
        self.DRAW_SIM = False
        self.LOG_PLOTS = True
        self.USE_THREADS = False
        self.CREATE_GIF = False
        self.USE_PROCESS = False
        
        self.SEED = None
        self.N_BOTS = 7
        self.START_LOC_LIST_XY = None
        self.START_CENTROID_LIST_XY = None 
        
        # Define the size of the walls
        self.GRID_THICKNESS = 10
        # Define the size of the screen
        self.COLS = 50
        self.ROWS = 50

        self.SCREEN_WIDTH = self.COLS * self.GRID_THICKNESS
        self.SCREEN_HEIGHT = self.ROWS * self.GRID_THICKNESS
        # Define the minimum and maximum sizes for the rooms
        self.MIN_ROOM_SIZE = 10 * self.GRID_THICKNESS
        self.MAX_ROOM_SIZE = 20 * self.GRID_THICKNESS

        # The Ground truth map is a 2D array of booleans
        self.MINE = 2.0
        self.EMPTY = 1.0
        self.OBSTACLE = 0.0

        # Map location definitions for agent_map
        self.UNKNOWN = -1
        self.KNOWN_WALL = 0
        self.KNOWN_EMPTY = 1
        self.FRONTIER = 2

        # Types of robot loss
        self.ROBOT_LOSS_TYPE = "None"
        self.MINE_DENSITY = .1

        # Define the colors to be used in the drawing
        self.BACKGROUND_COLOR = (78, 157, 157)
        self.WALL_COLOR = (80, 24, 99)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (251, 233, 89)
        self.PINK = (255, 0, 255)
        self.ORANGE = (255, 165, 0)
        self.PURPLE = (128, 0, 128)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.TEAL = (0, 128, 128)