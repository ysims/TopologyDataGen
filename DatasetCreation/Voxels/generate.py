import os
import yaml
import itertools
import numpy as np
import open3d as o3d

from Voxels3d import Voxels3d

path = os.path.join(os.getcwd(), 'data')

try:
    os.mkdir(path)
except OSError:
    print ("Directory %s exists." % path)

for j in range(3,8):
    for k in range(2,8):
        for i in range(50):
            voxels = Voxels3d(30)
            voxels.add_objects(j,k)
            
            # Get the objects
            grid = voxels.get_objects()

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
            with open(os.path.join(path,'{i}{j}{k}_betti.yaml'.format(i=i,j=j,k=k)), 'w') as file:
                documents = yaml.dump(voxels.get_betti(), file)
            o3d.io.write_point_cloud(os.path.join(path,"{i}{j}{k}_grid.ply".format(i=i,j=j,k=k)), o3d_point_cloud)

            print("\r-> Data added: ", i, "/50")
        print("----> End k: ", k, "/8")
    print("-------------> End j:", j, "/8")

