import numpy as np

from grid import Grid


def manhattan_distance(node_from, node_to):
    return abs(node_from.row - node_to.row) + abs(node_from.column - node_to.column)


def euclidean_distance(node_from, node_to):
    return np.sqrt((node_from.row - node_to.row) ** 2 + (node_from.column - node_to.column) ** 2)


def diagonal_distance(node_from, node_to):
    dx = abs(node_from.column - node_to.column)
    dy = abs(node_from.row - node_to.row)
    return (dx + dy) + (np.sqrt(2) - 2) * min(dx, dy)


def zero_distance(*args):
    return 0


def get_random_grid(random_seed=1, grid_name='test_grid', p_cnt=0.4, height=20, width=35):
    np.random.seed(random_seed)
    random_grid_cells = np.random.uniform(size=height * width).reshape(height, width) < p_cnt
    with open(f'{grid_name}.npy', 'wb+') as file_to_save_grid:
        np.save(file_to_save_grid, random_grid_cells)

    task_grid = Grid(height=height, width=width)
    task_grid.set_grid_from_array(random_grid_cells)

    return task_grid
