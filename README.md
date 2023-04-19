# Multi_Agents_Area_Exploration

In each agent's horizon, following labels will be created that will affect bidding for the neighbors:
- Empty     -> Positively affect
- Visited   -> Negatively affect
- Wall      -> Negatively affect
- Agent     -> Negatively affect


SETUP:

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
