import numpy
import pygame
import variables as var

class Cell:
    def __init__(self, row, column):
        
        self.row = row
        self.column = column
        self.agent = False          # is there any agent over a cell
        self.agent_id = None        # which agent is placed on a box 
        self.distance_matrix = None

    def draw(self, win, color):
        pygame.draw.rect(win,
                        color,
                        [(var.MARGIN + var.CELL_WIDTH) * self.column + var.MARGIN,
                        (var.MARGIN + var.CELL_HEIGHT) * self.row + var.MARGIN,
                        var.CELL_WIDTH,
                        var.CELL_HEIGHT])

    def calc_distance_matrices(self):
        x_arr, y_arr = numpy.mgrid[0:var.ROWS, 0:var.COLUMNS]
        cell = (self.row, self.column)
        dists = numpy.sqrt((x_arr - cell[0])**2 + (y_arr - cell[1])**2)
        return dists