import numpy as np

from src.point_utils.point_find import *

def recursive_look_for_neighbors(point, ground_truth_map, cfg, other_agents_locations, level):
    main_point_for_checking = point
    other_agents_locations.remove(main_point_for_checking)
    # check also even if the spot might be empty, there might be another agent already previously placed there
    if (ground_truth_map[main_point_for_checking[1], main_point_for_checking[0]] == cfg.EMPTY) and (main_point_for_checking not in other_agents_locations):
        return (True, main_point_for_checking)
    
    if level > 5:
        raise Exception("🛑🔎 recursive look_for_Neighbors level is too high")
    
    # checking neighbors with different levels starting from 1
    neighbors = findNeighbors(ground_truth_map, main_point_for_checking, level)

    for cur_point in neighbors:
        if cur_point[0] < 0 or cur_point[0] >= cfg.MAP_NP_ROWS or cur_point[1] < 0 or cur_point[1] >= cfg.MAP_NP_ROWS:
            # shift the point to be in the map
            cur_point = (max(1, min(cur_point[0], cfg.MAP_NP_ROWS-2)), max(1, min(cur_point[1], cfg.MAP_NP_ROWS-2)))

        # check if the point is not on an obstacle
        if (ground_truth_map[cur_point[1], cur_point[0]] == cfg.OBSTACLE):
            continue
        if cur_point in other_agents_locations:
            continue
        if ground_truth_map[cur_point[1], cur_point[0]] == cfg.EMPTY:
            return (True, cur_point)
        
    print(f"WARNING: level {level} All the neighbors are obstacles or off the map!! Here are the neighbors: ", neighbors)
    other_agents_locations.append(main_point_for_checking)
    return recursive_look_for_neighbors(point, ground_truth_map, cfg, other_agents_locations, level+1)

def check_if_valid_point(point, ground_truth_map, cfg, other_agents_locations):

    return recursive_look_for_neighbors(point, ground_truth_map, cfg, other_agents_locations, level=1)

def check_all_points(locations, ground_truth_map, cfg):

    locations = [(int(np.round(point[0])), int(np.round(point[1]))) for point in locations]
    new_locations = []
    for i, point in enumerate(locations):
        (found_point, new_p) = check_if_valid_point(point, ground_truth_map, cfg, locations)
        locations.insert(i, new_p)
        new_locations.append(new_p)
        if not found_point:
            # at this point, all the neighbors are obstacles or your off the map warning
            print("!!WARNING!!: All the neighbors are obstacles or your off the map current point: ", new_p)
            # get the closest point to the edge
            empty_points_rc = np.argwhere(ground_truth_map == cfg.EMPTY)
            goal_xy = get_closest_point_rc(empty_points_rc, new_p)
            print("new closest point to the edge: ", new_p)
            
    return new_locations


def Manual_Start(cfg, ground_truth_map):
    import warnings
    warnings.warn("Manual_Start lets you place points at any location")
    return [(2, 7), (9, 16), (2, 5), (3, 11)]

def Rand_Start(cfg, ground_truth_map):
    locations =[]
    for i in range(cfg.N_BOTS):
        cur_loc = get_random_point(ground_truth_map, cfg)
        while cur_loc in locations:
            cur_loc = get_random_point( ground_truth_map, cfg)

        locations.append(cur_loc)
    return locations

def Center_Start(cfg, ground_truth_map):
    locations= points_over_radious(cfg.MAP_NP_ROWS, cfg.MAP_NP_ROWS, cfg.N_BOTS, 'center')
    locations = check_all_points(locations, ground_truth_map, cfg)
    return locations

def Top_Left_Start(cfg, ground_truth_map):
    locations = points_over_radious(cfg.MAP_NP_ROWS, cfg.MAP_NP_ROWS, cfg.N_BOTS, 'topleft')
    locations = check_all_points(locations, ground_truth_map, cfg)
    return locations

def Edge_Start(cfg, ground_truth_map):
    locations = points_on_rectangle_edge(cfg.MAP_NP_ROWS, cfg.MAP_NP_ROWS, cfg.N_BOTS, )
    locations = check_all_points(locations, ground_truth_map, cfg)
    return locations

def Distributed_Start(cfg, ground_truth_map):
    locations = dividegrid(cfg.MAP_NP_ROWS, cfg.MAP_NP_ROWS, cfg.N_BOTS)
    locations = check_all_points(locations, ground_truth_map, cfg)
    return locations
            