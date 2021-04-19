import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D # <--- This is important for 3d plotting 
from Voxels3d import Voxels3d
import math

voxels = Voxels3d([30, 30, 30])
voxels.addObjects(3)
voxels.checkIntersectFull()

output = voxels.getObjects()

# set the colors of each object
colors = np.empty(output.shape, dtype=object)
colors[output] = 'blue'

# and plot everything
ax = plt.figure().add_subplot(projection='3d')
ax.voxels(output, edgecolor='k')

plt.show()