import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D # <--- This is important for 3d plotting 
from Voxels3d import Voxels3d
import math
import itertools
import random
import open3d as o3d

# voxel_dataset = []
 

# for j in range(3,8):
#     for k in range(2,8):
#         for i in range(50):
#             voxels = Voxels3d(30)
#             voxels.add_objects(j,k)
#             voxel_dataset.append(voxels.get_objects())
#             print("-> Data added: ", i, "/50")
#     print("----> End k: ", k, "/8")
# print("-------------> End j:", j, "/8")


# for i,j in itertools.combinations(voxel_dataset,2):
#     if not (i ^ j).any():
#         print("THE SAME!")

# plotting
# for i in voxel_dataset:
#     ax = plt.figure().add_subplot(projection='3d')
#     ax.voxels(i, edgecolor='k')
# plt.show()

# Create the voxel grid with some objects and lines
voxels = Voxels3d(30)
voxels.add_objects(2,5)

# Get the objects
grid = voxels.get_objects()

# Create a numpy array from the voxel grid so we can turn it into an open3d geometry
points = None
for X,Y,Z in itertools.product(range(0, 30), repeat=3):
    if (grid[X][Y][Z]):
        if type(points) is np.ndarray:
            points = np.concatenate((points,[[X,Y,Z]]),axis=0)
        else:
            points = np.array([[X, Y, Z]])

ax = plt.axes(projection='3d')
ax.scatter3D(points[:,0], points[:,1], points[:,2])
plt.show()


# Create a PointCloud from the array and then convert it to a VoxelGrid
o3d_point_cloud = o3d.geometry.PointCloud()
o3d_point_cloud.points = o3d.utility.Vector3dVector(points)
o3d_voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(o3d_point_cloud, 1)
# o3d.io.write_point_cloud("./test.ply", o3d_point_cloud)

o3d.visualization.draw_geometries([o3d_voxel_grid])
