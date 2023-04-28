# Multi_Agents_Area_Exploration

This project is investigating how to explore a building map that is not known prior except its boundaries. It considers following approaches for the agents while they acting for the next step during iterations. (Frontier Closest, Frontier Random, Unknown Closest, and Unknown Random)

## SETUP:

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

## RUN:

to run  the simulation, run the following command:
```
python main.py
```

if you would like to change the simulation parameters, you can do so by changing the values in the `parameters_cfg.py` file.


### Simulation Parameters:


| Parameter | Description | Default Value |
| --- | --- | --- |
| `Debug` | Debug mode, renders a GUI | False |
| `Use_process` | Use multiprocessing | False |
| `Create_gif` | Create gif, Debug must be True to run this | False |
| `agent_count_list` | List of agent counts to run the simulation with | `[2,4,6]` or `list(range(4,12,4))` |
| `iteration_repeat_experiment` | Number of times to repeat the experiment | `1` or `list(range(0, 60))` |
|`min_rom_size` | Minimum size of the room | `30` or `list( range(4,10,2))` |
|`Method_list` | A list of all the Methods that the simulation will run, these all hihareate from the base `Agent` class | - |
|`Start_scenario_list`|||
|`Start_Goal_list`|||
|`Robot_Loss`|||

| Method | Description | 
| --- | --- |
| Frontier_Random | Each agent randomly selects a frontier section of the map to explore. |
| Frontier_Closest | Each agent selects the closest frontier section of the map to explore. |
| Unknown_Random | Each agent randomly selects an unknown section of the map to explore. |
| Unknown_Closest | Each agent selects the closest unknown section of the map to explore. |
| Voronoi_Frontier_Random | The map is split up into various sections and then the frontier random method is used within each section. |
| Voronoi_Frontier_Closest | The map is split up into various sections and then the frontier closest method is used within each section.|
| Voronoi_Frontier_Help_Closest | The map is split up into various sections and then the frontier closest method is |
| Voronoi_Frontier_Help_Random | |
| Decision_Frontier_Closest | |
| DarpVorOnly | |
| DarpMST | |
| Decay_Epsilon_Greedy_Unknown | |
| Decay_Epsilon_Greedy_Frontier | |
| Epsilon_Greedy_Unknown | |
| Epsilon_Greedy_Frontier | |
| GameTheory | |
| Heterogenus | |



# Optimal Stopping

The code for the optimal stopping is found on the branch NoSharedMap. 

This section of the project implemented an optimal stopping algorithm to see how much of the map each individual agent would need to explore before the map is completely covered.
 
The algorithm is as follows:

- The agents have no communication ability, meaning they no longer know where other agents have explored
- The agents are randomly placed throughout the map and explore the closest frontier
- The agents each individually explore a predefined percentage of the map and stop once they have achieved their predetermined coverage
    - Once all agents are done, the total area coverage between all bots is computed


This allows us to see at what point the agents can stop exploring because they have collectively explored the entire region. This delves into an area of unexplored robotics where we can optimize exploration tasks where there is no or minimal communication. The future 
        


## What is this project about?
In each agent's horizon, following labels will be created that will affect bidding for the neighbors:
- Empty     -> Positively affect
- Visited   -> Negatively affect
- Wall      -> Negatively affect
- Agent     -> Negatively affect