import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D # <--- This is important for 3d plotting 
from Voxels3d import Voxels3d
import math
import itertools
import random

voxel_dataset = []
 

for j in range(3,8):
    for k in range(2,8):
        for i in range(50):
            voxels = Voxels3d(30)
            voxels.add_objects(j,k)
            voxel_dataset.append(voxels.get_objects())
            print("-> Data added: ", i, "/50")
    print("----> End k: ", k, "/8")
print("-------------> End j:", j, "/8")


for i,j in itertools.combinations(voxel_dataset,2):
    if not (i ^ j).any():
        print("THE SAME!")

# plotting
# for i in voxel_dataset:
#     ax = plt.figure().add_subplot(projection='3d')
#     ax.voxels(i, edgecolor='k')
# plt.show()

# voxels = Voxels3d(30)
# voxels.add_objects(5,2)


# ax = plt.figure().add_subplot(projection='3d')
# ax.voxels(voxels.get_objects(), edgecolor='k')
# plt.show()