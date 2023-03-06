import sys
import random
import math
import pygame
from pygame.locals import QUIT
import psutil

pygame.init()
size = (400, 400)
surf = pygame.display.set_mode((size[0], size[1]))
surf.fill((100, 100, 100))
points = []
pygame.display.set_caption('Voronoi Diagram')

while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                sim_start_time = psutil.Process().cpu_times().user



                for i in range(20):
                    posx = random.randint(0, 399)
                    posy = random.randint(0, 399)
                    points.append([[posx, posy], (random.randint(1, 254), random.randint(1, 254), random.randint(1, 254))])
                    # pygame.draw.circle(surf, (255, 255, 255), (posx, posy), 1, 1)
                    for x, y in [(x, y) for x in range(size[0]) for y in range(size[1])]:
                        # print(x,y)
                        if surf.get_at((x, y))[:-1] != (255, 255, 255):
                            surf.set_at((x, y), min([(math.sqrt((x - i[0][0])**2 + (y - i[0][1])**2), i[1]) for i in points])[1])




                end_time = psutil.Process().cpu_times().user
                print("Tot time=", end_time - sim_start_time)


            

        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()