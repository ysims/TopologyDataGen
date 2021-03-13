import numpy as np
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import itertools
import math
from ripser import ripser
from persim import plot_diagrams
import random

# Returns the distance between coord1 and coord2. Both coordinates are 3d cartesian coordinates.
def dist3d(coord1, coord2):
    return math.sqrt(math.pow((coord1[0] - coord2[0]), 2) + math.pow((coord1[1] - coord2[1]), 2) + math.pow((coord1[2] - coord2[2]), 2))

# Create a cube with side length 'length' represented as a point cloud, with lengthxlengthxlenth points in it. 
# Each point is set at each integer point (e.g. (6,1,0)), with some noise. 
# The maximum distance that each point can be displaced from its original integer position is 'noise'
def create_cube(length, noise):
    data = []
    for x in range(0,length+1):
        for y in range(0,length+1):
            for z in range(0,length+1):
                random = [(np.random.random() - 0.5) * noise * 2, (np.random.random() - 0.5) * noise * 2, (np.random.random() - 0.5) * noise * 2] 
                data.append([x + random[0], y + random[1], z + random[2]])
    return data


# Given a circle centered on 'point' with radius 'radius',
# does it intersect with another circle defined previously, or the boundary
# point: list of three elements
# radius: float
# circles: list of lists with two elements, the first of which is a point and the second is a radius
# boundary: the circle cannot intersect or touch the area outside of the object it is appearing inside. boundary is a float representing the length of the cube.
def does_circle_intersect(point, radius, circles, boundary):
    # Check intersection for all circles
    for circle in circles:
        # Add the radiuses, adding a point extra as a boundary. This is the minimum distance between the center points, to not intersect
        min_distance = radius + circle[1] + 1 
        # Check if the distance between them is too small
        if dist3d(circle[0], point) < min_distance:
            return True
    # Check if it goes over the boundary
    for coord in point:
        if (coord - radius) < 1 or (coord + radius) > (boundary-1):
            return True
    # If we got through all the checks ok, return false
    return False

def remove_circle(data, point, radius):
    indices = []
    for index,item in enumerate(data):
        # Get the distance between this point and the center of the circle
        distance = dist3d(item,point)
        if distance <= radius:
            indices.append(index)
    return np.delete(data, indices, 0)

square_size = 7
noise = 0.1
max_circles = 100
max_radius = 3

# Create the cube as a numpy array
data = np.array(create_cube(square_size, noise))

# Remove circles
# n_circles = int(np.random.random() * (max_circles + 1))   # Add 1 since random does not include 1
n_circles = max_circles
i = 0   # Counter for our while loop. Will only increment if we can add a circle.
circles = []
shuffled_data = np.copy(data)
random.shuffle(shuffled_data)

while i < n_circles:
    for item in shuffled_data:
        found_something = False
        radius = np.random.random() * (max_radius - 1) + 1
        point = item
        # print('check', radius, point)
        # Create a random circle
        if not does_circle_intersect(point, radius, circles, square_size):
            # print('passed')
            data = remove_circle(data, point, radius)
            circle = [point, radius]
            circles.append(circle)
            i = i + 1
            found_something = True
            # print('after',radius)
            print(i,'/',n_circles,'Removing circle with center point', circle, 'with radius', radius)
            if i >= n_circles:
                break
    if not found_something:
        print('Couldn\'t place that many holes!', i,'/',n_circles)
        break

# Plot the data points
ax = plt.axes(projection='3d')
ax.scatter3D(data[:,0], data[:,1], data[:,2])
plt.show()

print('Computing topology')

# Calculate the persistent homology
diagrams = ripser(data, maxdim=3)['dgms']

# Plot the persistent homology
plot_diagrams(diagrams, show=True)