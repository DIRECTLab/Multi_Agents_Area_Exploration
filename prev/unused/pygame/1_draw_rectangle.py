import sys
import pygame
from pygame.locals import KEYDOWN, K_q

# CONSTANTS:
SCREENSIZE = WIDTH, HEIGHT = 600, 400
BLACK = (0, 0, 0)
GREY = (160, 160, 160)
PADDING = PAD_VERTICAL, PAD_HORIZONTAL = 60, 60
# VARS:
_VARS = {'surf': False}


def main():
    pygame.init()
    _VARS['surf'] = pygame.display.set_mode(SCREENSIZE)
    while True:
        checkEvents()
        _VARS['surf'].fill(GREY)
        drawRect()
        pygame.display.update()


def drawRect():
    # There's a native way to draw a rectangle in pygame,
    # this is just to explain how lines can be drawn.
    # TOP lEFT TO RIGHT
    pygame.draw.line(
      _VARS['surf'], BLACK,
      (0 + PAD_HORIZONTAL, 0 + PAD_VERTICAL),
      (WIDTH - PAD_HORIZONTAL, 0 + PAD_VERTICAL), 2)
    # BOTTOM lEFT TO RIGHT
    pygame.draw.line(
      _VARS['surf'], BLACK,
      (0 + PAD_HORIZONTAL, HEIGHT - PAD_VERTICAL),
      (WIDTH - PAD_HORIZONTAL, HEIGHT - PAD_VERTICAL), 2)
    # LEFT TOP TO BOTTOM
    pygame.draw.line(
      _VARS['surf'], BLACK,
      (0 + PAD_HORIZONTAL, 0 + PAD_VERTICAL),
      (0 + PAD_HORIZONTAL, HEIGHT - PAD_VERTICAL), 2)
    # RIGHT TOP TO BOTTOM
    pygame.draw.line(
      _VARS['surf'], BLACK,
      (WIDTH - PAD_HORIZONTAL, 0 + PAD_VERTICAL),
      (WIDTH - PAD_HORIZONTAL, HEIGHT - PAD_VERTICAL), 2)


def checkEvents():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_q:
            pygame.quit()
            sys.exit()


if __name__ == '__main__':
    main()