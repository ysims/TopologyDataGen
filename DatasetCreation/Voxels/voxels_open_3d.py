import open3d as od3
from Voxels3d import Voxels3d
import numpy as np

my_voxels = Voxels3d(30)
my_voxels.add_objects(0,1)

voxels = od3.geometry.VoxelGrid().create_dense(origin=np.array([0,0,0]), color=np.array([0,0,0]), voxel_size=1, width=30, height=30, depth=30)
print(dir(od3.geometry.VoxelGrid))

print(voxels.get_voxel([30,30,30]))
voxels.clear()
print(voxels.get_voxel([30,30,30]))

pointcloud = od3.geometry.PointCloud()
print(dir(od3.geometry.PointCloud))
print(pointcloud.points)

trianglemesh = od3.geometry.TriangleMesh()
print(dir(od3.geometry.TriangleMesh))