import argparse
import itertools
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D # <--- This is important for 3d plotting 
import numpy as np
import time

from BettiCube import BettiCube

# Add command line arguments
parser = argparse.ArgumentParser(description=
    "This program creates and draws a single cavity-filled cube")
parser.add_argument("--cube_size", type=int, default=50,
                    help="Size of the cavity-filled cube, cubed.")
parser.add_argument("--spheroid_num", type=int, default=0,
                    help="Number of spheroid cavities to add to the cube.")
parser.add_argument("--torus_num", type=int, default=0,
                    help="Number of torus cavities to add to the cube.")
parser.add_argument("--torus2_num", type=int, default=0,
                    help="Number of two-holed torus cavities to add to the cube.")
parser.add_argument("--island_num", type=int, default=0,
                    help="Number of island cavities to add to the cube.")
parser.add_argument("--tunnel_num", type=int, default=0,
                    help="Number of tunnel cavities to add to the cube.")
parser.add_argument("--octopus_num", type=int, default=0,
                    help="Number of octopus cavities to add to the cube.")
args = parser.parse_args()

# Create the dictionary to print and use when making objects
dict = {
    "Spheroid": args.spheroid_num,
    "Torus": args.torus_num,
    "Torus2": args.torus2_num,
    "Island": args.island_num,
    "Tunnel": args.tunnel_num,
    "Octopus": args.octopus_num,
}

print("Adding: ", dict) # print for debugging purposes

start_time = time.time()    # begin time count

voxels = BettiCube(args.cube_size)            # make the cube
voxels.add_objects(dict)            # add the right number of objects
grid = voxels.get_full_objects()    # get the objects

print("Adding --------- %s seconds ---" % (time.time() - start_time)) # print how long it took

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