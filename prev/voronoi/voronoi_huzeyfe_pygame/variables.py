AGENT_COUNT = 100
COLUMNS = 400
ROWS = 400
CELL_WIDTH = 1
CELL_HEIGHT = 1

MARGIN = 1
WINDOW_WIDTH = COLUMNS * (CELL_WIDTH + MARGIN) + MARGIN
WINDOW_HEIGHT = ROWS * (CELL_HEIGHT + MARGIN) + MARGIN
COLOR_BLACK = (0,0,0)
COLOR_GRAY = (50,50,50)
COLOR_GREEN = (0,255,0)
matrix_list, coming_set, colors, grid = list(), list(), list(), list()
agent_locs = set()