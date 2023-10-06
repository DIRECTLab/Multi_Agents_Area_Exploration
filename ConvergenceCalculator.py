import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os.path import exists

for l in [2, 4, 6, 8, 10, 12, 14, 16]:
    # for start in ["Edge", "Rand", "Top_Left"]:
    for start in ["Top_Left"]:
        all_searched_areas = []
        complexities = []
        for k in [3,6,9,12,15,27,65]:
            searched_areas = []
            files = [f"./new_data100/multiple_method_search_data/start_scenario_{start}_Start_Position/goal_scenario_Edge_Start_Goal/bots-{l}_min-room-size{k}.0/seed-{j}_100explored_Exploration.csv" for j in range(100, 150, 1)]
            result = []
            for file in files:
                if exists("" + file):
                    result.append(pd.read_csv("" + file))
                # else:
                #     print("file doesn't exist:" + file)
            if(result == []):
                continue
            all_files = pd.concat(result)
            for i in range(1,99,1):
                map_complexity = all_files.loc[i, 'map_complexity'].mean()
                total_searched_area = all_files.loc[i, 'total_explored'].mean()
                searched_areas.append(total_searched_area)
            complexities.append(map_complexity)
            # print("completed k=" + str(k))
            all_searched_areas.append(searched_areas)

            # searched_areas
            # map_complexity

        average_values = np.mean(all_searched_areas, axis=0)

        for i in range(average_values.size):
            if(average_values[i] > 0.95):
                print(f"start= {start}, bots={l}, individual exploration={i}, total explored={average_values[i]}")
                break
    #     plt.plot([x for x in range(1,99,1)], average_values * 100, label=f"{l} agents {start} start")
    #     # plt.legend().set_title("# of Agents")
    #     # plt.plot([x for x in range(self.T)], self.hawk_population_history, label="Hawk Population")
    #     # plt.plot([x for x in range(self.T)], self.total_population_history, label="Total Population")
    # plt.xlabel("Defined stopping point")
    # plt.ylabel("Percent Explored")
    # plt.legend()
    # plt.savefig(f"./averagegraph_{l}-bots_all-start-types.png")
    # plt.clf()
    # plt.show()