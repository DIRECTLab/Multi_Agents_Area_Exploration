ASANA BOARD DISCUSSIONS
------------------------
### Purpose of Research
Search or Coverage or xxxxxxx
I think main purpose of the research is exploring unknown regions and create the geometry of the building using multiple agents.
How different theories(bid, voronoi, random, radial) would perform in order to cover a region fully in an unknown space?

### What is the scope of inter robot communication and map communication?
Here will be the assumptions regarding inter robot communication and map communication:
- No GPS available inside of the buildings
- Each agent knows its location. In each iteration, it moves the next best neighbor to move on among its neighbors.

### Will we do a hardware set?
No. Main purpose of the research will be focusing on comparing different versions of area exploration methods and how quickly they would find an object using these methods.
### Will we do a robotic simulation?
We do not need that since the paper will be mostly algorithmic and will be focusing on comparing the success of different methods.
### Will we run this in a continuous environment or grid based world?
From my perspective, we should continue working with the grid space but eventually design and test this system with the continuous environment as well before we do the hardware tests.







Bidding
    having different vision horizons: Say 2, robot take the best action to move in its neighbors. Using the horizon, we label each seen cell with labels. (Open, Wall, Visited, Agent)
Randomized
    even though it will have different horizons: Randomized agent will take a randomized action to move among its neighbors.
Voronoi
    divide the region among agents
    generate a path plan asssuming the region is empty
Radial
    send agents to different part of the buildings

