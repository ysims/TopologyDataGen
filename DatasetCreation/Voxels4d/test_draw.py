import itertools
import numpy as np

from HyperCube import HyperCube

size = 50           # size of the hypercube (to the fourth power)
tunnel_num = 0
torus_num = 0
torus2_num = 0
sphere_num = 1
island_num = 0

# Create the dictionary to print and use when making objects
dict = {
    # "tunnel": tunnel_num,
    # "torus": torus_num,
    # "torus2": torus2_num,
    "sphere": sphere_num,
    # "island": island_num,
}

print("Adding: ", dict) # print for debugging purposes

voxels = HyperCube(size)            # make the cube
voxels.add_objects(dict)            # add the right number of objects
grid = voxels.get_objects()    # get the objects

# Create a numpy array from the voxel grid so we can save it to use later
numpy_point_cloud = None
for X,Y,Z,W in itertools.product(range(0, size), repeat=4):
    if (grid[X][Y][Z][W]):
        if type(numpy_point_cloud) is np.ndarray:
            numpy_point_cloud = np.concatenate((numpy_point_cloud,[[X,Y,Z,W]]),axis=0)
        else:
            numpy_point_cloud = np.array([[X, Y, Z, W]])

np.save('4d_objects', numpy_point_cloud)
