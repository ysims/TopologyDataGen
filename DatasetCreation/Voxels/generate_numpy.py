import os
import yaml
import itertools
import numpy as np
import random

from BettiCube import BettiCube

path = os.path.join(os.getcwd(), 'data')

# Create the directory to store the data
try:
    os.mkdir(path)
except OSError:
    print ("Directory %s exists." % path)

size = 50           # size of the cube (cubed)
num_objects = 100    # highest number of one object in any one image
repeat_objects = 100    # number of times we repeat on a given number of objects

object = 'tunnels'  # the type of object that will be generated


count = 0   # for file naming

# loop over all configurations of # of object from 0 to 10 for all objects
for i in range(num_objects):
    for j in range(repeat_objects):
        if i == 0:
            continue
        # Set all values to 0, the one we will generate will be changed after
        tunnel_num = 0
        torus_num = 0
        torus2_num = 0
        sphere_num = 0
        island_num = 0

        if object == 'tunnels':
            tunnel_num = i
        elif object == 'torus':
            torus_num = i
        elif object == 'torus2':
            torus2_num = i
        elif object == 'sphere':
            sphere_num = i
        elif object == 'island':
            island_num = i

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

        # Create a numpy array from the voxel grid
        numpy_point_cloud = None
        for X,Y,Z in itertools.product(range(0, 30), repeat=3):
            if (grid[X][Y][Z]):
                if type(numpy_point_cloud) is np.ndarray:
                    numpy_point_cloud = np.concatenate((numpy_point_cloud,[[X,Y,Z]]),axis=0)
                else:
                    numpy_point_cloud = np.array([[X, Y, Z]])

        # Write our data
        with open(os.path.join(path,'{count}_betti.yaml'.format(count=count)), 'w') as file:
            documents = yaml.dump(voxels.get_data(), file)
        np.save(os.path.join(path,"{count}_grid.ply".format(count=count)), numpy_point_cloud)

        count += 1  # increment our naming counter

        print("Created data:", count)


# ax = plt.figure().add_subplot(projection='3d')
# ax.voxels(voxels.get_objects(), edgecolor='k')
# plt.show()