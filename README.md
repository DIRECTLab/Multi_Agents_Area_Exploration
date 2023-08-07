# Multi Agents Area Exploration

## Quick Summary

This project is investigating how to explore an unknown building that its boundaries are known in prior. To analyze the efficiency of various exploration strategies, we generated sixteen different exploration method that is being used by the system homogenously as well as different starting and goal conditions. It is assumed that a reliable communication and map localization occurs in the background without considerable errors.

Furthermore, we also examined how agent loss would affect the overall performance by placing mines over the ground.

## Installation of the Environment:

```
git clone https://github.com/DIRECTLab/Multi_Agents_Area_Exploration.git
cd Multi_Agents_Area_Exploration/
conda create -y --name multiagent python==3.9.2
conda activate multiagent
pip install \
	numpy==1.23.3 \
	opencv-python==4.6.0.66 \
    opencv-contrib-python==4.6.0.66 \
	pygame==2.3.0 \
	scipy==1.10.1 \
	jupyter_client==7.0.6 \
    jupyter_core==5.3.0 \
    numba==0.56.4 \
    pillow==9.2.0 \
    scikit-learn==1.2.2 \
    matplotlib==3.5.3 \
    pandas==1.4.4 \
    tqdm==4.64.1 \
    psutil==5.9.4
```

## Running the Program:

To run  the simulation, run the following command:
```
python main.py
```

If you would like to change the simulation parameters, you can do so by changing the values in the `parameters_cfg.py` file.


### Simulation Parameters:


| Parameter | Description | Default Value |
| --- | --- | --- |
| `Debug` | Debug mode, renders a GUI | `False` |
| `Create_gif` | Create gif, Debug must be True to run this | `False` |
| `agent_count_list` | List of agent counts to run the simulation with | `[2,4,6]` or `list(range(4,12,4))` |
| `iteration_repeat_experiment` | Number of times to repeat the experiment | `1` or `list(range(0, 60))` |
| `min_rom_size` | Minimum size of the room | `30` or `list( range(4,10,2))` |
| `Method_list` | A list of all the Methods that the simulation will run, these all inherit from the base `Agent` class | - |
| `Start_scenario_list`| starting locations for all the agents | `Manual_Start`, `Rand_Start`, `Edge_Start`, `Top_Left_Start`, `Center_Start`, `Distributed_Start` |
| `Start_Goal_list`| initial goal locations | `Manual_Start`, `Rand_Start`, `Edge_Start`, `Top_Left_Start`, `Center_Start`,  `Distributed_Start`, |
| `Robot_Loss`| Holds a list of classes that change the scenario, where `Agent` is a normal run, `Unrecoverable` the robots will hit random mines and become disabled, and last the `Disrepair` robots can help and fix other robots | `[Agent, Unrecoverable, Disrepair]` |


| Method | Description |
| --- | --- |
| `Frontier_Random` | Each agent randomly selects a frontier section of the map to explore. ||
| `Frontier_Closest` | Each agent selects the closest frontier section of the map to explore. ||
| `Unknown_Random` | Each agent randomly selects an unknown section of the map to explore. ||
| `Unknown_Closest` | Each agent selects the closest unknown section of the map to explore. ||
| `Voronoi_Frontier_Random` | The map is split up into various sections and then the frontier random method is used within each section. ||
| `Voronoi_Frontier_Closest` | The map is split up into various sections and then the frontier closest method is used within each section. ||
| `Voronoi_Frontier_Help_Closest` | The map is split up into various sections and then the frontier closest method is used in tandem with the paired searching strategy. ||
| `Voronoi_Frontier_Help_Random` | The map is split up into various sections and then the frontier random method is used in tandem with the paired searching strategy.||
| `Voronoi_Unknown_Help_Closest` | The map is split up into various sections and then the unknown closest method is used in tandem with the paired searching strategy. ||
| `Voronoi_Unknown_Help_Random` | The map is split up into various sections and then the unknown random method is used in tandem with the paired searching strategy.||
| `Decision_Frontier_Closest` | Each agent shares it's goal position in the mutual data set. As each agent sets a new goal position it checks to see if any other agent is already visiting that location. If not, it keeps that location. If it is already taken \|then the agent with the shortest path keeps that location and the other is assigned a new goal.||
| `Decay_Epsilon_Greedy_Unknown` | Each agent is assigned to either random or closest exploration of a frontier based on an epsilon value. As the simulation progresses the epsilon value decays resulting in less exploration as the map is explored more. ||
| `Decay_Epsilon_Greedy_Frontier` | Each agent is assigned to either random or closest exploration of an unknown area based on an epsilon value. As the simulation progresses the epsilon value decays resulting in less exploration as the map is explored more.||
| `Epsilon_Greedy_Unknown` | Each agent is assigned to either random or closest exploration of an unknown area based on a constant epsilon value.||
| `Epsilon_Greedy_Frontier` | Each agent is assigned to either random or closest exploration of a frontier based on a constant epsilon value.||
| `GameTheory` | Allowing each agent to choose the anti-majority of search methods chosen by the other agents. The two options are random or closest.||
