import sys
import pygame
from pygame.locals import KEYDOWN, K_q

# CONSTANTS:
SCREENSIZE = WIDTH, HEIGHT = 600, 400
BLACK = (0, 0, 0)
GREY = (160, 160, 160)
# GLOBAL VARS, Using a Dictionary.
_VARS = {'surf': False}

# This is the main game loop, it constantly runs until you press the Q KEY
# or close the window.
# CAUTION: THis will run as fast as you computer allows,
# if you need to set a specific FPS look at tick methods.


def main():
    pygame.init()  # Initial Setup
    _VARS['surf'] = pygame.display.set_mode(SCREENSIZE)
    # The loop proper, things inside this loop will
    # be called over and over until you exit the window
    while True:
        checkEvents()
        _VARS['surf'].fill(GREY)
        drawLine()
        pygame.display.update()


def drawLine():
    # draw a diagonal line from top left coordinates 0,0
    # to bottom right with coordinates 600 (Width), 400 (Height)
    pygame.draw.line(_VARS['surf'], BLACK, (0, 0), (WIDTH, HEIGHT), 2)


def checkEvents():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_q:
            pygame.quit()
            sys.exit()


if __name__ == '__main__':
    main()