import random as r
import math as m
import psutil
import sys

def makeMap(numPoints, mapSize):
    # Generate random colors so I can see what's happened.
    colors = []
    for color in range(4):
        print(color)
        colors.append(color)
    # Generate the base points.
    ct = 0
    
    # basePoints = []
    # for point in range(numPoints):
    #     x = r.randint(0, mapSize)
    #     y = r.randint(0, mapSize)
    #     # print(x,y)
    #     basePoints.append((x, y, colors[ct]))
    #     ct += 1

    basePoints = [(5, 5, 0), (5, 15, 1), (15, 5, 2), (15, 15, 3)]
    print(basePoints)

    
    # Generate all the other points on the map.
    points = []
    for x in range(mapSize):
        for y in range(mapSize):
            distance = mapSize * 2
            for bp in basePoints:
                newDistance = m.sqrt(((x - bp[0]) ** 2) + ((y - bp[1]) ** 2))
                if newDistance < distance:
                    distance = newDistance
                    color = bp[2]
            # print([x, y, color])
            points.append([x, y, color])
    return points
    



def main():    
    # sim_start_time = psutil.Process().cpu_times().user
    points = makeMap(4, 20)
    print(points)

    # for p in points:
    #     gfxdraw.pixel(surf, p[0], p[1], p[2])






    
    # end_time = psutil.Process().cpu_times().user
    # print("Tot time=", end_time - sim_start_time)
    #     pygame.display.flip()
if __name__ == "__main__":
    main()
