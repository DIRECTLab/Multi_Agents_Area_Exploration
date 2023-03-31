import numpy as np
import sys
import cv2
from src.darp.Visualization import darp_area_visualization
import time
import random
import os
from numba import njit

np.set_printoptions(threshold=sys.maxsize)

random.seed(1)
os.environ['PYTHONHASHSEED'] = str(1)
np.random.seed(1)

@njit(fastmath=True)
def assign(droneNo, rows, cols, GridEnv, MetricMatrix, A):

    ArrayOfElements = np.zeros(droneNo)
    for i in range(rows):
        for j in range(cols):
            if GridEnv[i, j] == -1:
                minV = MetricMatrix[0, i, j]
                indMin = 0
                for r in range(droneNo):
                    if MetricMatrix[r, i, j] < minV:
                        minV = MetricMatrix[r, i, j]
                        indMin = r

                A[i, j] = indMin
                ArrayOfElements[indMin] += 1

            elif GridEnv[i, j] == -2:
                A[i, j] = droneNo
    return A, ArrayOfElements

@njit(fastmath=True)
def inverse_binary_map_as_uint8(BinaryMap):
    # cv2.distanceTransform needs input of dtype unit8 (8bit)
    return np.logical_not(BinaryMap).astype(np.uint8)

@njit(fastmath=True)
def euclidian_distance_points2d(array1: np.array, array2: np.array) -> np.float_:
    # this runs much faster than the (numba) np.linalg.norm and is totally enough for our purpose
    return (((array1[0] - array2[0]) ** 2) + ((array1[1] - array2[1]) ** 2)) ** 0.5

@njit(fastmath=True)
def constructBinaryImages(labels_im, robo_start_point, rows, cols):
    BinaryRobot = np.copy(labels_im)
    BinaryNonRobot = np.copy(labels_im)
    for i in range(rows):
        for j in range(cols):
            if labels_im[i, j] == labels_im[robo_start_point]:
                BinaryRobot[i, j] = 1
                BinaryNonRobot[i, j] = 0
            elif labels_im[i, j] != 0:
                BinaryRobot[i, j] = 0
                BinaryNonRobot[i, j] = 1

    return BinaryRobot, BinaryNonRobot

@njit(fastmath=True)
def CalcConnectedMultiplier(rows, cols, dist1, dist2, CCvariation):
    returnM = np.zeros((rows, cols))
    MaxV = 0
    MinV = 2**30

    for i in range(rows):
        for j in range(cols):
            returnM[i, j] = dist1[i, j] - dist2[i, j]
            if MaxV < returnM[i, j]:
                MaxV = returnM[i, j]
            if MinV > returnM[i, j]:
                MinV = returnM[i, j]

    for i in range(rows):
        for j in range(cols):
            returnM[i, j] = (returnM[i, j]-MinV)*((2*CCvariation)/(MaxV - MinV)) + (1-CCvariation)

    return returnM


class DARP:
    def __init__(self,
                grid_row,                       # 5
                grid_column,                    # 5
                robot_initial_positions,        # [0, 2, 4]
                obstacle_positions,             # [7, 8]
                equal_portions=False,           # default
                portions=[0.2, 0.3, 0.5],       # default (0.33, 0.33, 0.33)
                visualization=False,            # False
                MaxIter=80000,                  # default
                CCvariation=0.01,               # default
                randomLevel=0.0001,             # default
                dcells=2,                       # default
                importance=False):              # default

        self.rows = grid_row
        self.cols = grid_column
        self.initial_positions, self.obstacles_positions, self.portions = self.sanity_check(robot_initial_positions, portions, obstacle_positions, equal_portions)
        # print("self.initial_positions, self.obstacles_positions, self.portions", self.initial_positions, self.obstacles_positions, self.portions)
        self.equal_portions = equal_portions
        self.visualization = visualization

        # not sure what the below values are for except MaxIter
        self.MaxIter = MaxIter
        self.CCvariation = CCvariation
        self.randomLevel = randomLevel
        self.dcells = dcells
        self.importance = importance

        # print("\nInitial Conditions Defined As Follows:")
        # print("Grid Dimensions:", grid_row, grid_column)
        # print("Initial Robots' positions", self.initial_positions)
        # print("Number of Robots:", len(self.initial_positions))
        print("Portions for each Robot:", self.portions, "\n")

        self.robotNumber = len(self.initial_positions)
        # self.A holds the agents positions except the first one which is used for the connection
        self.A = np.zeros((self.rows, self.cols))
        # self.GridEnv defines the world with -1(default), and -2(obstacles)
        self.GridEnv = self.defineGridEnv()

        # connectivity matrices for each agent initialized with full of zeros
        self.connectivity = np.zeros((self.robotNumber, self.rows, self.cols), dtype=np.uint8)
        # binary robot regions defined initially with full of zero values in bool format(False)
        self.BinaryRobotRegions = np.zeros((self.robotNumber, self.rows, self.cols), dtype=bool)
        self.ArrayOfElements = np.zeros(self.robotNumber)
        self.color = []
        self.distance_matrices, self.threshold_value, self.number_of_cells, self.desirable_cell_count_fer, self.cell_importance_values, self.min_importance_fer, self.max_importance_fer = self.construct_Assignment_Matrix()
        # print(  "\n\n\ndistance matrices for each agent:\n", self.distance_matrices, 
        #         "\nthreshold value that we accept for the specific grid which is given:\n", self.threshold_value, 
        #         "\ntotal number of cells for the grid:\n", self.number_of_cells, 
        #         "\ndesirable cell count for each robot:\n", self.desirable_cell_count_fer, 
        #         "\ncell importance matrices for each agent:\n", self.cell_importance_values, 
        #         "\nminimum importance value for each agent:\n", self.min_importance_fer, 
        #         "\nmaximum importance value for each agent:\n", self.max_importance_fer)

        # assign one color to each agent
        for r in range(self.robotNumber):
            np.random.seed(r)
            self.color.append(list(np.random.choice(range(256), size=3)))
        
        np.random.seed(1)
        if self.visualization:
            self.assignment_matrix_visualization = darp_area_visualization(self.A, self.robotNumber, self.color, self.initial_positions)








    # converting the agent, obstacle and portions into something which is more clear to continue running on
    def sanity_check(self, given_initial_positions, given_portions, obs_pos, equal_portions):
        initial_positions = []
        for position in given_initial_positions:
            if position[0] < 0 or position[1] < 0 or position[0] >= self.rows or position[1] >= self.cols:
                print("Initial positions should be inside the Grid.")
                sys.exit(1)
            initial_positions.append(position)

        obstacles_positions = []
        for obstacle in obs_pos:
            if obstacle[0] < 0 or obstacle[1] < 0 or obstacle[0] >= self.rows or obstacle[1] >= self.cols:
                print("Obstacles should be inside the Grid.")
                sys.exit(2)
            obstacles_positions.append(obstacle)

        portions = []
        if equal_portions:
            portions = given_portions
        else:
            for drone in range(len(initial_positions)):
                portions.append(1 / len(initial_positions))

        if len(initial_positions) != len(portions):
            print("Portions should be defined for each drone")
            sys.exit(3)

        s = sum(portions)
        if abs(s - 1) >= 0.0001:
            print("Sum of portions should be equal to 1.")
            sys.exit(4)

        for position in initial_positions:
            for obstacle in obstacles_positions:
                if position[0] == obstacle[0] and position[1] == obstacle[1]:
                    print("Initial positions should not be on obstacles")
                    sys.exit(5)

        return initial_positions, obstacles_positions, portions

    # -1 for initial default value
    # -2 for obstacle positions
    def defineGridEnv(self):
        GridEnv = np.full(shape=(self.rows, self.cols), fill_value=-1)  # create non obstacle map with value -1
        
        # obstacle tiles value is -2
        for idx, obstacle_pos in enumerate(self.obstacles_positions):
            GridEnv[obstacle_pos[0], obstacle_pos[1]] = -2

        connectivity = np.zeros((self.rows, self.cols))
        
        mask = np.where(GridEnv == -1)
        connectivity[mask[0], mask[1]] = 255
        image = np.uint8(connectivity)
        num_labels, labels_im = cv2.connectedComponents(image, connectivity=4)

        if num_labels > 2:
            print("The environment grid MUST not have unreachable and/or closed shape regions")
            sys.exit(6)
        
        # initial robot tiles will have their array.index as value
        for idx, robot in enumerate(self.initial_positions):
            GridEnv[robot] = idx
            self.A[robot] = idx

        return GridEnv

    # Construct Assignment Matrix
    def construct_Assignment_Matrix(self):
        number_of_cells = self.rows*self.cols
        fair_division = 1/self.robotNumber
        effectiveSize = number_of_cells - self.robotNumber - len(self.obstacles_positions)
        threshold_value = 0

        if effectiveSize % self.robotNumber != 0:
            threshold_value = 1

        desirable_cell_count_fer = np.zeros(self.robotNumber)
        MaximunDist = np.zeros(self.robotNumber)
        max_importance_fer = np.zeros(self.robotNumber)
        min_importance_fer = np.zeros(self.robotNumber)

        for i in range(self.robotNumber):
            desirable_cell_count_fer[i] = effectiveSize * self.portions[i]
            min_importance_fer[i] = sys.float_info.max
            if (desirable_cell_count_fer[i] != int(desirable_cell_count_fer[i]) and threshold_value != 1):
                threshold_value = 1

        distance_matrices = np.zeros((self.robotNumber, self.rows, self.cols))
        cell_importance_values = np.zeros((self.robotNumber, self.rows, self.cols))

        for x in range(self.rows):
            for y in range(self.cols):
                tempSum = 0
                for r in range(self.robotNumber):
                    distance_matrices[r, x, y] = euclidian_distance_points2d(np.array(self.initial_positions[r]), np.array((x, y))) # E!
                    if distance_matrices[r, x, y] > MaximunDist[r]:
                        MaximunDist[r] = distance_matrices[r, x, y]
                    tempSum += distance_matrices[r, x, y]

                for r in range(self.robotNumber):
                    if tempSum - distance_matrices[r, x, y] != 0:
                        cell_importance_values[r, x, y] = 1/(tempSum - distance_matrices[r, x, y])
                    else:
                        cell_importance_values[r, x, y] = 1
                    # Todo FixMe!
                    if cell_importance_values[r, x, y] > max_importance_fer[r]:
                        max_importance_fer[r] = cell_importance_values[r, x, y]

                    if cell_importance_values[r, x, y] < min_importance_fer[r]:
                        min_importance_fer[r] = cell_importance_values[r, x, y]

        return distance_matrices, threshold_value, number_of_cells, desirable_cell_count_fer, cell_importance_values, min_importance_fer, max_importance_fer











    def divideRegions(self):
        success = False
        cancelled = False
        criterionMatrix = np.zeros((self.rows, self.cols))
        iteration = 0

        while self.threshold_value <= self.dcells and not success and not cancelled:
            downThres = (self.number_of_cells - self.threshold_value*(self.robotNumber-1))/(self.number_of_cells*self.robotNumber)
            upperThres = (self.number_of_cells + self.threshold_value)/(self.number_of_cells*self.robotNumber)
            success = True
            # Main optimization loop
            iteration = 0

            while iteration <= self.MaxIter and not cancelled:
                self.A, self.ArrayOfElements = assign(self.robotNumber, self.rows, self.cols, self.GridEnv, self.distance_matrices, self.A)
                ConnectedMultiplierList = np.ones((self.robotNumber, self.rows, self.cols))
                ConnectedRobotRegions = np.zeros(self.robotNumber)
                plainErrors = np.zeros((self.robotNumber))
                divFairError = np.zeros((self.robotNumber))
                self.update_connectivity()
                for r in range(self.robotNumber):
                    ConnectedMultiplier = np.ones((self.rows, self.cols))
                    ConnectedRobotRegions[r] = True
                    num_labels, labels_im = cv2.connectedComponents(self.connectivity[r, :, :], connectivity=4)
                    if num_labels > 2:
                        ConnectedRobotRegions[r] = False
                        BinaryRobot, BinaryNonRobot = constructBinaryImages(labels_im, self.initial_positions[r], self.rows, self.cols)
                        ConnectedMultiplier = CalcConnectedMultiplier(self.rows, self.cols,
                                                                        self.NormalizedEuclideanDistanceBinary(True, BinaryRobot),
                                                                        self.NormalizedEuclideanDistanceBinary(False, BinaryNonRobot), self.CCvariation)
                    ConnectedMultiplierList[r, :, :] = ConnectedMultiplier
                    plainErrors[r] = self.ArrayOfElements[r]/(self.desirable_cell_count_fer[r]*self.robotNumber)
                    if plainErrors[r] < downThres:
                        divFairError[r] = downThres - plainErrors[r]
                    elif plainErrors[r] > upperThres:
                        divFairError[r] = upperThres - plainErrors[r]
                if self.IsThisAGoalState(self.threshold_value, ConnectedRobotRegions):
                    break
                TotalNegPerc = 0
                totalNegPlainErrors = 0
                correctionMult = np.zeros(self.robotNumber)
                for r in range(self.robotNumber):
                    if divFairError[r] < 0:
                        TotalNegPerc += np.absolute(divFairError[r])
                        totalNegPlainErrors += plainErrors[r]
                    correctionMult[r] = 1
                for r in range(self.robotNumber):
                    if totalNegPlainErrors != 0:
                        if divFairError[r] < 0:
                            correctionMult[r] = 1 + (plainErrors[r]/totalNegPlainErrors)*(TotalNegPerc/2)
                        else:
                            correctionMult[r] = 1 - (plainErrors[r]/totalNegPlainErrors)*(TotalNegPerc/2)
                        criterionMatrix = self.calculateCriterionMatrix(self.cell_importance_values[r],
                                                                        self.min_importance_fer[r],
                                                                        self.max_importance_fer[r],
                                                                        correctionMult[r],
                                                                        divFairError[r] < 0)
                    self.distance_matrices[r] = self.FinalUpdateOnMetricMatrix(criterionMatrix,
                                                                                self.generateRandomMatrix(),
                                                                                self.distance_matrices[r],
                                                                                ConnectedMultiplierList[r, :, :])
                iteration += 1
                if self.visualization:
                    self.assignment_matrix_visualization.placeCells(self.A, iteration_number=iteration)
                    # time.sleep(0.2)
                    time.sleep(0.001)
            
            if iteration >= self.MaxIter:
                self.MaxIter = self.MaxIter/2
                success = False
                self.threshold_value += 1

        self.getBinaryRobotRegions()
        return success, iteration

    def getBinaryRobotRegions(self):
        ind = np.where(self.A < self.robotNumber)
        temp = (self.A[ind].astype(int),)+ind
        self.BinaryRobotRegions[temp] = True

    def generateRandomMatrix(self):
        RandomMatrix = np.zeros((self.rows, self.cols))
        RandomMatrix = 2*self.randomLevel*np.random.uniform(0, 1,size=RandomMatrix.shape) + (1 - self.randomLevel)
        return RandomMatrix

    def FinalUpdateOnMetricMatrix(self, CM, RM, currentOne, CC):
        MMnew = np.zeros((self.rows, self.cols))
        MMnew = currentOne*CM*RM*CC
        return MMnew

    def IsThisAGoalState(self, thresh, connectedRobotRegions):
        for r in range(self.robotNumber):
            if np.absolute(self.desirable_cell_count_fer[r] - self.ArrayOfElements[r]) > thresh or not connectedRobotRegions[r]:
                return False
        return True

    def update_connectivity(self):
        self.connectivity = np.zeros((self.robotNumber, self.rows, self.cols), dtype=np.uint8)
        for i in range(self.robotNumber):
            mask = np.where(self.A == i)
            self.connectivity[i, mask[0], mask[1]] = 255

    def calculateCriterionMatrix(self, cell_importance_values, min_importance_fer, max_importance_fer, correctionMult, smallerthan_zero):
        returnCrit = np.zeros((self.rows, self.cols))
        if self.importance:
            if smallerthan_zero:
                returnCrit = (cell_importance_values- min_importance_fer)*((correctionMult-1)/(max_importance_fer-min_importance_fer)) + 1
            else:
                returnCrit = (cell_importance_values- min_importance_fer)*((1-correctionMult)/(max_importance_fer-min_importance_fer)) + correctionMult
        else:
            returnCrit[:, :] = correctionMult

        return returnCrit

    def NormalizedEuclideanDistanceBinary(self, RobotR, BinaryMap):
        distRobot = cv2.distanceTransform(inverse_binary_map_as_uint8(BinaryMap), distanceType=2, maskSize=0, dstType=5)
        MaxV = np.max(distRobot)
        MinV = np.min(distRobot)
        #Normalization
        if RobotR:
            distRobot = (distRobot - MinV)*(1/(MaxV-MinV)) + 1
        else:
            distRobot = (distRobot - MinV)*(1/(MaxV-MinV))
        return distRobot







if __name__ == '__main__':
    # darp_instance = DARP(10, 10, [0, 3, 9], [5, 6, 7], False, [0.2, 0.3, 0.5], True)
    # darp_instance = DARP(5, 5, [0, 2, 4], [7, 8], False, [0.2, 0.3, 0.5], True)
    
    # darp_instance = DARP(grid_row, grid_column, agent_positions, obstacle_positions)
    darp_instance = DARP(5, 5, [(0,0), (0,2), (0,4)], [(1,2), (1,3)])
    # Divide areas based on robots initial positions
    darp_success , iterations = darp_instance.divideRegions()
    
    if darp_success:
        print("Success...", "Iteration count is:", iterations)
        print("Agents", darp_instance.BinaryRobotRegions)
    else:
        print("Problem occurred...")