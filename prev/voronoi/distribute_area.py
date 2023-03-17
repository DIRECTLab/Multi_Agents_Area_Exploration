import numpy as np
import matplotlib.pyplot as plt

def calc_closest_factors(c: int):
    if c//1 != c:
        raise TypeError("c must be an integer.")
    a, b, i = 1, c, 0
    while a < b:
        i += 1
        if c % i == 0:
            a = i
            b = c//a
    return [b, a]

def dividegrid(rows, cols, n):
    agent_count = n
    turned_list = calc_closest_factors(int(agent_count))
    # print(f"turned list is {turned_list}")
    agentrowcount = turned_list[0]
    agentcolumncount = turned_list[1]
    # print(f"agentrowcount {agentrowcount}")
    # print(f"agentcolumncount {agentcolumncount}")
    x = np.arange(0, cols, cols/agentcolumncount)
    y = np.arange(0, rows, rows/agentrowcount)
    x_var = []
    y_var = []
    for i in x:
        for j in y:
            print((int(i),int(j)))
            x_var.append(i)
            y_var.append(j)
    x_offset = (x_var[2] - x_var[0])/2
    y_offset = (y_var[1] - y_var[0])/2
    x_var = [int(x + x_offset) for x in x_var]
    y_var = [int(y + y_offset) for y in y_var]
    print("x_var2", x_var)
    print("y_var2", y_var)
    points = []
    for i in range(len(x_var)):
        points.append((x_var[i], y_var[i]))
    print(points)
    # plt.plot(x_var,y_var)
    # plt.scatter(x_var,y_var)
    # plt.show()


def main():
    dividegrid(20,20,8)

if __name__ == "__main__":
    main()