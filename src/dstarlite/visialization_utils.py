# from sys import float_info
from PIL import Image, ImageDraw

# EPS = float_info.epsilon

def get_image(  grid_map,
                start_node=None,
                goal_node=None,
                traveled_path=None,
                planned_path=None,
                scale=30,
                draw_current_position=True,
                draw_observed_range=True):
    """
    Get PIL image for the agents state:
        - start, goal position
        - walls that are observed by the agent
        - path that is already travelled
        - planned path to the goal on the current agent position
    :param grid_map: Grid
    :param start_node: Node
    :param goal_node: Node
    :param traveled_path: list[tuple(int, int)]
    :param planned_path: list[tuple(int, int)]
    :param scale: int
    :param draw_current_position : bool
    :param draw_observed_range : bool
    :return: PIL.Image
    """
    hIm = grid_map.height * scale
    wIm = grid_map.width * scale
    image = Image.new('RGB', (wIm, hIm), color=(205,205,205))
    draw = ImageDraw.Draw(image)

    # draw grid with walls
    for row in range(grid_map.height):
        for column in range(grid_map.width):
            if grid_map.is_wall_cell_observed[row][column]:
                draw.rectangle((
                    column * scale,
                    row * scale,
                    (column + 1) * scale - 1,
                    (row + 1) * scale - 1
                ), fill=(109,109,109))
            elif grid_map.is_passable_cell_observed[row][column]:
                draw.rectangle((
                    column * scale,
                    row * scale,
                    (column + 1) * scale - 1,
                    (row + 1) * scale - 1
                ), fill=(255, 255, 255))


    # draw start and goal positions
    for node, fill_value in [(start_node, (130,236,134)), (goal_node, (255,147,134))]:
        if (node is not None) and (grid_map.is_traversable(node.row, node.column)):
            draw.rectangle((
                node.column * scale,
                node.row * scale,
                (node.column + 1) * scale - 1,
                (node.row + 1) * scale - 1
            ), fill=fill_value, width=0)

    # draw paths
    for path, color in [(traveled_path, 'green'), (planned_path, 'red')]:
        if len(path) > 1:
            scaled_path = [((column + 0.5) * scale, (row + 0.5) * scale) for row, column in path]
            draw.line(scaled_path, fill=color, width=3, joint='curve')

    # draw current position
    current_position = traveled_path[-1]
    if draw_current_position:
        draw.ellipse((
            current_position[1] * scale,
            current_position[0] * scale,
            (current_position[1] + 1) * scale - 1,
            (current_position[0] + 1) * scale - 1
        ), fill='blue', width=0)

    # draw observe range for current position
    if draw_observed_range:
        draw.rectangle((
            (current_position[1] - 2) * scale,          # column-left
            (current_position[0] - 2) * scale,          # row-up
            (current_position[1] + 3) * scale - 1,      # column-right
            (current_position[0] + 3) * scale - 1       # row-down
        ), fill=None, width=3, outline='blue')

    return image
