import pygame
import random
import psutil


SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
COLOR_MIN_VALUE = 0
COLOR_MAX_VALUE = 255
MASSIVE_VALUE = 9999999999999999999999999999999999999999999999999
LEFT = 1
RIGHT = 3

gameDisplay = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
list_of_positions = []
random.seed()


def recolor():
    pixelarray = pygame.PixelArray(gameDisplay)

    if len(list_of_positions) > 0:
        for i in range(0, SCREEN_WIDTH):
            for j in range(0, SCREEN_HEIGHT):
                min_distance = MASSIVE_VALUE
                index = 0
                for k in range(0, len(list_of_positions)):
                    temp_x, temp_y, temp_color = list_of_positions[k]
                    if min_distance > ((temp_x - i) * (temp_x - i) + (temp_y - j) * (temp_y - j)):
                        min_distance = ((temp_x - i) * (temp_x - i) + (temp_y - j) * (temp_y - j))
                        index = k

                temp_x, temp_y, temp_color = list_of_positions[index]
                pixelarray[i][j] = temp_color


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                sim_start_time = psutil.Process().cpu_times().user




                
                for i in range(20):
                    y = random.randint(0, 399)
                    x = random.randint(0, 399)
                    color = (random.randint(COLOR_MIN_VALUE, COLOR_MAX_VALUE), random.randint(COLOR_MIN_VALUE, COLOR_MAX_VALUE),
                            random.randint(COLOR_MIN_VALUE, COLOR_MAX_VALUE))
                    list_of_positions.append((x, y, color))
                    recolor()
                end_time = psutil.Process().cpu_times().user







                print("Tot time=", end_time - sim_start_time)
    pygame.display.update()
