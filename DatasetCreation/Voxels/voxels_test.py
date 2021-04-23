import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D # <--- This is important for 3d plotting 
from Voxels3d import Voxels3d
import math
import itertools

voxel_dataset = []

for i in range(100):
    voxels = Voxels3d([30,30,30])
    voxels.add_objects(3)
    voxel_dataset.append(voxels.get_objects())
    voxels.check_intersect_full()


for i,j in itertools.combinations(voxel_dataset,2):
    if not (i ^ j).any():
        print("THE SAME!")

# plotting
# for i in voxel_dataset:
#     ax = plt.figure().add_subplot(projection='3d')
#     ax.voxels(i, edgecolor='k')


# plt.show()