import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os.path import exists

for l in [2,4,6,8,10,12,14,16]:
    all_searched_areas = []
    complexities = []
    for k in [3,6,9,12,15,18,21,24,27,30]:
        searched_areas = []
        files = [f"./new_data50/multiple_method_search_data/start_scenario_Edge_Start_Position/goal_scenario_Edge_Start_Goal/bots-{l}_min-room-size{k}.0/seed-{j}_100explored_Exploration.csv" for j in range(50, 100, 1)]
        result = [] 
        for file in files:
            if exists("" + file):
                result.append(pd.read_csv("" + file))
            else:
                print("file doesn't exist:" + file)
        if(result == []):
            continue
        all_files = pd.concat(result)
        for i in range(1,99,1):
            map_complexity = all_files.loc[i, 'map_complexity'].mean()
            total_searched_area = all_files.loc[i, 'total_explored'].mean()
            searched_areas.append(total_searched_area)
        complexities.append(map_complexity)
        print("completed k=" + str(k))
        all_searched_areas.append(searched_areas)

        # searched_areas
        # map_complexity

    average_values = np.mean(all_searched_areas, axis=0)
        
    plt.plot([x for x in range(1,99,1)], average_values * 100, label=f"{l} agents")
    # plt.legend().set_title("# of Agents")
    # plt.plot([x for x in range(self.T)], self.hawk_population_history, label="Hawk Population")
    # plt.plot([x for x in range(self.T)], self.total_population_history, label="Total Population")
    plt.xlabel("Defined stopping point")
    plt.ylabel("Combined Exploration Percentage")
plt.plot([0, 100], [99, 99], 'r--')
plt.grid(True, linestyle='--')
plt.legend()
plt.savefig(f"./averagegraph_edge-start.png")
    # plt.show()