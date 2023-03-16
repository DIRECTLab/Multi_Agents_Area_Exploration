import numpy as np
import matplotlib.pyplot as plt

MATRIX_ROWS = 20
MATRIX_COLUMNS = 20


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


matrix = np.zeros((MATRIX_ROWS,MATRIX_COLUMNS))
print(matrix)
vari = input("how many agents are going to be placed onto the grid:")
turned_list = calc_closest_factors(int(vari))
# print(f"turned list is {turned_list}")
agentrowcount = turned_list[0]
agentcolumncount = turned_list[1]
print(f"agentrowcount {agentrowcount}")
print(f"agentcolumncount {agentcolumncount}")


x = np.arange(0, MATRIX_COLUMNS, MATRIX_COLUMNS/agentcolumncount)
y = np.arange(0, MATRIX_ROWS, MATRIX_ROWS/agentrowcount)
print(x, y)




x_var = []
y_var = []
for i in x:
    for j in y:
        x_var.append(i)
        y_var.append(j)


print("x_var1", x_var)
print("y_var1", y_var)

x_offset = (x_var[2] - x_var[0])/2
y_offset = (y_var[1] - y_var[0])/2
x_var = [x + x_offset for x in x_var]
y_var = [y + y_offset for y in y_var]
print("x_var2", x_var)
print("y_var2", y_var )

# plt.plot(x_var,y_var)
plt.scatter(x_var,y_var)
plt.show()