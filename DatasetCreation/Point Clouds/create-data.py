import numpy as np
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import itertools
import math
from ripser import ripser
from persim import plot_diagrams
import random
from PointCloud import PointCloud

# # Returns the distance between coord1 and coord2, removing the third dimension. Both coordinates are 3d cartesian coordinates.
# def dist2d(coord1, coord2):
#     return math.sqrt(math.pow((coord1[1] - coord2[1]), 2) + math.pow((coord1[2] - coord2[2]), 2))

# # Ratio: (0,1). The higher, the greater the [filled] hole in the center.
# def remove_tori(data, point, radius_outer, radius_inner):
#     indices = []
#     for index,item in enumerate(data):
#         # Get the distance between this point and the center of the sphere
#         distance = dist3d(item,point)
#         if distance <= radius:
#             distance_2d = dist2d(item, point)
#             if distance_2d > radius_inner:
#                 indices.append(index)
#     return np.delete(data, indices, 0)

square_size = 35
max_spheres = 20
max_radius = 10
min_radius = 5

radius_outer = 16
radius_inner = 5
point = np.array([15, 15, 15])
direction = np.array([1, 1, 1])
height = 15

# Create the cube as a numpy array
cube = PointCloud(3, 35, 0.1)
# cube.remove_spheres(max_spheres, max_radius, min_radius)
cube.remove_torus(point, direction, radius_inner, radius_outer, height)

data = cube.get_data()

# with open('data.txt', 'w') as f:
#     for item in data:
#         f.write("%s\n" % item)

# Plot the data points
ax = plt.axes(projection="3d")

# plt.plot(data[:,0],data[:,1], 'o')

# slice = 17
# start = slice * (square_size * square_size)
# if start != 0:
#     start = start + 1
# end = (slice+1) * (square_size * square_size)

# ax.scatter3D(data[start:end,0], data[start:end,1], data[start:end,2])
# ax.scatter3D(data[:, 0], data[:, 1], data[:, 2])
# plt.show()

print("Computing topology")

# Calculate the persistent homology
diagrams = ripser(data, maxdim=3)["dgms"]

# # Plot the persistent homology
plot_diagrams(diagrams, show=True)
