import numpy as np
import itertools
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D # <--- This is important for 3d plotting 

from BettiCube import BettiCube

size = 50           # size of the cube (cubed)
tunnel_num = 0
torus_num = 0
torus2_num = 0
sphere_num = 0
island_num = 0

# Create the dictionary to print and use when making objects
dict = {
    "tunnel": tunnel_num,
    "torus": torus_num,
    "torus2": torus2_num,
    "sphere": sphere_num,
    "island": island_num,
}

print("Adding: ", dict) # print for debugging purposes

voxels = BettiCube(size)            # make the cube
voxels.add_objects(dict)            # add the right number of objects
grid = voxels.get_full_objects()    # get the objects

# Create a numpy array from the voxel grid so we can print it
numpy_point_cloud = None
for X,Y,Z in itertools.product(range(0, 30), repeat=3):
    if (grid[X][Y][Z]):
        if type(numpy_point_cloud) is np.ndarray:
            numpy_point_cloud = np.concatenate((numpy_point_cloud,[[X,Y,Z]]),axis=0)
        else:
            numpy_point_cloud = np.array([[X, Y, Z]])

# Plot the grid
ax = plt.figure().add_subplot(projection='3d')
ax.voxels(voxels.get_objects(draw=True), edgecolor='k')
plt.show()