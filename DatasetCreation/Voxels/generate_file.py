import os
import itertools
import numpy as np
import random

from BettiCube import BettiCube

size = 100           # size of the cube (cubed)

# Create the dictionary to print and use when making objects
dict = {
    "torus2": 3,
    "torus": 4,
    "sphere": 3,
    "island": 0,
    "tunnel": 20,
}
print("Adding: ", dict) # print for debugging purposes

voxels = BettiCube(size)    # make the cube
voxels.add_objects(dict)    # add the right number of objects
grid = voxels.get_objects(draw=True)    # get the objects

# Create a numpy array from the voxel grid so we can turn it into an open3d geometry
numpy_point_cloud = None
for X,Y,Z in itertools.product(range(0, size), repeat=3):
    if (grid[X][Y][Z]):
        if type(numpy_point_cloud) is np.ndarray:
            numpy_point_cloud = np.concatenate((numpy_point_cloud,[[X,Y,Z]]),axis=0)
        else:
            numpy_point_cloud = np.array([[X, Y, Z]])

np.save('objects', numpy_point_cloud)

grid = voxels.get_full_objects()    # get the objects

# Create a numpy array from the voxel grid so we can turn it into an open3d geometry
numpy_point_cloud = None
for X,Y,Z in itertools.product(range(0, 30), repeat=3):
    if (grid[X][Y][Z]):
        if type(numpy_point_cloud) is np.ndarray:
            numpy_point_cloud = np.concatenate((numpy_point_cloud,[[X,Y,Z]]),axis=0)
        else:
            numpy_point_cloud = np.array([[X, Y, Z]])

np.save('cube', numpy_point_cloud)
