import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os.path import exists

for l in [2,4,6,8,10,12,14,16]:
    all_searched_areas = []
    complexities = []
    for k in [3,6,9,12,15,18,30]:
        missing_files = 0
        searched_areas = []
        files = [f"./required_steps50/multiple_method_search_data/start_scenario_Rand_Start_Position/goal_scenario_Edge_Start_Goal/bots-{l}_min-room-size{k}.0/seed-{j}_100explored_Exploration.csv" for j in range(50,100, 1)]
        result = []
        for file in files:
            if exists("" + file):
                result.append(pd.read_csv("" + file))
            else:
                # print("file doesn't exist:" + file)
                missing_files += 1
        if(result == []):
            continue
        all_files = pd.concat(result)
        for i in range(1,99,1):
            map_complexity = all_files.loc[i, 'map_complexity'].mean()
            total_searched_area = all_files.loc[i, 'required_steps'].mean()
            searched_areas.append(total_searched_area)
        complexities.append(map_complexity)
        print(" bots=" + str(l) + "room_size= " + str(k))
        print("missing files=" + str(missing_files))
        all_searched_areas.append(searched_areas)

    # searched_areas
    # map_complexity
    smallest_complexity = min(complexities)
    for searched_area in all_searched_areas:
        value = format(complexities.pop(0) - smallest_complexity, ".3f")
        plt.plot(searched_area, [x for x in range(1,99,1)], label=f"{value}")
        plt.legend().set_title("Map Complexity")

    # num = 0
    # counter = [i for i in range(1,99,1)]
    # for i in [3,6,9,12,15,27]:
    #     combined_data = np.array([counter, all_searched_areas[num]]).T
    #     np.savetxt(f"./required_steps_complexity{i}_{l}botgraph_top_left-start.csv", combined_data, delimiter=",", fmt='%s')
    #     num+=1
    # plt.plot([x for x in range(self.T)], self.hawk_population_history, label="Hawk Population")
    # plt.plot([x for x in range(self.T)], self.total_population_history, label="Total Population")
    # plt.title(f"Optimal stopping point for {l} agents")
    plt.plot([180, 180], [0, 100],'r--', label='Horizontal Line at y=3')
    plt.ylabel("Combined Exploration Percentage")
    plt.xlabel("Total Steps")
    plt.grid(True, linestyle='--')
    plt.savefig(f"./required_steps_{l}botgraph_rand-start.png")
    plt.clf()
    # plt.show()