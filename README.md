# Multi_Agents_Area_Exploration

install following libraries through pip or in a conda environment:

pip install pygame

pip install numpy


In this branch, I will be working on increasing the vision horizon from 1 to multiple (2,3...)

In each agent's horizon, following labels will be created that will affect bidding for the neighbors:
- Empty     -> Positively affect
- Visited   -> Negatively affect
- Wall      -> Negatively affect
- Agent     -> Negatively affect

