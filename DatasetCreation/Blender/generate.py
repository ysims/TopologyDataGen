import os
import yaml
import itertools
import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D # <--- This is important for 3d plotting 
# import open3d as o3d
import random

from BettiCube import BettiCube

import bpy  # import blender python
import bmesh    # import blender mesh


# Reset the scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Get the scene
scene = bpy.context.scene

# Empty mesh
mesh = bpy.data.meshes.new("My Cube")

# Make the cube object
cube = bpy.data.objects.new("My Cube", mesh)

# Add object to a collection in the scene
# scene.collection.objects.link(cube)

# Build a cube mesh using bmesh, Blender's mesh editing system
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)

# Store the bmesh inside the mesh
bm.to_mesh(mesh)

# cube.location = (0,0,0)

size = 50           # size of the cube (cubed)
num_objects = 10    # highest number of one object in any one image

count = 426   # for file naming

# loop over all configurations of # of object from 0 to 10 for all objects
# for torus2_num, island_num, torus_num, sphere_num, tunnel_num in itertools.product(range(num_objects), repeat=5):
    # if tunnel_num + torus2_num + torus_num + sphere_num + island_num > 10:
    #     continue

    # if random.randrange(0, 2) is 0:
    #     continue

# Create the dictionary to print and use when making objects
dict = {
    "tunnel": 4,
    "torus": 1,
    "torus2": 1,
    "sphere": 0,
    "island": 0,
}
# print("Adding: ", dict) # print for debugging purposes

voxels = BettiCube(size)    # make the cube
voxels.add_objects(dict)    # add the right number of objects
grid = voxels.get_full_objects()    # get the objects

# Create a numpy array from the voxel grid so we can turn it into an open3d geometry
numpy_point_cloud = None
for X,Y,Z in itertools.product(range(0, 30), repeat=3):
    if (grid[X][Y][Z]):
        # Create the Blender cubes
        new_cube = cube.copy()
        scene.collection.objects.link(new_cube)
        new_cube.location = (i,j,k)

        if type(numpy_point_cloud) is np.ndarray:
            numpy_point_cloud = np.concatenate((numpy_point_cloud,[[X,Y,Z]]),axis=0)
        else:
            numpy_point_cloud = np.array([[X, Y, Z]])



# Create a PointCloud from the array and then convert it to a VoxelGrid
# o3d_point_cloud = o3d.geometry.PointCloud()
# o3d_point_cloud.points = o3d.utility.Vector3dVector(numpy_point_cloud)
# o3d_voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(o3d_point_cloud, 1)

# # Write our data
# with open(os.path.join(path,'{count}_betti.yaml'.format(count=count)), 'w') as file:
#     documents = yaml.dump(voxels.get_data(), file)
# o3d.io.write_voxel_grid(os.path.join(path,"{count}_grid.ply".format(count=count)), o3d_voxel_grid)

# count += 1  # increment our naming counter

# print("Created data:", count)


# ax = plt.figure().add_subplot(projection='3d')
# ax.voxels(voxels.get_objects(), edgecolor='k')
# plt.show()