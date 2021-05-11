import os
import yaml
import itertools
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D # <--- This is important for 3d plotting 
import open3d as o3d
import random

from BettiCube import BettiCube

path = os.path.join(os.getcwd(), 'data')

# Create the directory to store the data
try:
    os.mkdir(path)
except OSError:
    print ("Directory %s exists." % path)

size = 50           # size of the cube (cubed)
num_objects = 10    # highest number of one object in any one image

count = 426   # for file naming

# loop over all configurations of # of object from 0 to 10 for all objects
for torus2_num, island_num, torus_num, sphere_num, tunnel_num in itertools.product(range(num_objects), repeat=5):
    if tunnel_num + torus2_num + torus_num + sphere_num + island_num > 10:
        continue

    if random.randrange(0, 2) == 0:
        continue

    # Create the dictionary to print and use when making objects
    dict = {
        "tunnel": tunnel_num,
        "torus": torus_num,
        "torus2": torus2_num,
        "sphere": sphere_num,
        "island": island_num,
    }
    print("Adding: ", dict) # print for debugging purposes
    
    voxels = BettiCube(size)    # make the cube
    voxels.add_objects(dict)    # add the right number of objects
    grid = voxels.get_full_objects()    # get the objects

    # Create a numpy array from the voxel grid so we can turn it into an open3d geometry
    numpy_point_cloud = None
    for X,Y,Z in itertools.product(range(0, 30), repeat=3):
        if (grid[X][Y][Z]):
            if type(numpy_point_cloud) is np.ndarray:
                numpy_point_cloud = np.concatenate((numpy_point_cloud,[[X,Y,Z]]),axis=0)
            else:
                numpy_point_cloud = np.array([[X, Y, Z]])

    # Create a PointCloud from the array and then convert it to a VoxelGrid
    o3d_point_cloud = o3d.geometry.PointCloud()
    o3d_point_cloud.points = o3d.utility.Vector3dVector(numpy_point_cloud)
    o3d_voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(o3d_point_cloud, 1)

    # Write our data
    with open(os.path.join(path,'{count}_betti.yaml'.format(count=count)), 'w') as file:
        documents = yaml.dump(voxels.get_data(), file)
    o3d.io.write_voxel_grid(os.path.join(path,"{count}_grid.ply".format(count=count)), o3d_voxel_grid)

    count += 1  # increment our naming counter

    print("Created data:", count)


# ax = plt.figure().add_subplot(projection='3d')
# ax.voxels(voxels.get_objects(), edgecolor='k')
# plt.show()