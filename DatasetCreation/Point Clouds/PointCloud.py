import numpy as np
import itertools
import math
import random

# Returns Euclidean distance of two n-dimensional arrays.
# coord1 and coord2 should be the same length
def distanceXd(coord1, coord2):
    accum_sum = 0
    for point1,point2 in zip(coord1,coord2):
        accum_sum += math.pow((point1 - point2), 2)
    return math.sqrt(accum_sum)

# PointCloud represents a point cloud of a hypercube with holes in it. It is used to create data for machine learning.
# dimension: dimension of the hypercube. Eg square is 2d, cube is 3d.
# size: the number of points along one axis.
# data: n-dimensional array of m-dimensional arrays. m is equal to the dimension of the point cloud and n is equal to the size of the hypercube to the power of the dimension (size^dimension)
# spheres: array of hyperspheres represented each by a 2-dimensional array comprising of the center point (n-dimensional array) and the radius (float). these hyperspheres are the holes in the hypercube.
class PointCloud:

    # Create a hypercube with side length *size-1 represented as a point cloud, with *size^*dimension points in it. 
    # Each point is set at each integer point (e.g. (6,1,0)), with some noise (resulting in a float). 
    # The maximum distance that each value in a point can be displaced from its original integer position is *noise
    def __init__(self, dimension, size, noise):
        # Create the cube
        data = np.array(list(itertools.product(range(0, size), repeat=dimension))).astype(np.float32)
        # Add the noise
        for coord in range(len(data)):
            for point in range(len(data[coord])):
                random_noise = (np.random.random() - 0.5) * noise * 2
                data[coord][point] += random_noise

        self.dimension = dimension
        self.size = size
        self.data = data
        self.spheres = []

    # Given a hypersphere centered on *point with radius *radius, does it intersect with another hypersphere defined previously, or the boundary
    # point: list of *dimension elements
    # radius: float
    def does_sphere_intersect(self, point, radius):
        # Check intersection for all hyperspheres
        for sphere in self.spheres:
            # Add the radiuses, adding a point extra as a boundary. This is the minimum distance between the center points, to not intersect
            # Add one to ensure some space between them, enough to have at least a point layer of depth 1
            min_distance = radius + sphere[1] + 1 
            # Check if the distance between them is too small
            if distanceXd(sphere[0], point) < min_distance:
                return True
        # Check if it goes over the boundary
        for coord in point:
            if (coord - radius) < 1 or (coord + radius) > (self.size-2):
                return True
        # If we got through all the checks ok, return false
        return False

    # Remove a given hypersphere area from the hypercube. Must check that there is no intersecting beforehand, using does_sphere_intersect function
    def remove_sphere(self, point, radius):
        indices = []
        for index,item in enumerate(self.data):
            # Get the distance between this point and the center of the hypersphere
            distance = distanceXd(item,point)
            if distance <= radius:
                indices.append(index)
        self.data = np.delete(self.data, indices, 0)

    def remove_spheres(self, max_spheres, max_radius, min_radius):
        # Remove hyperspheres
        # n_spheres = int(np.random.random() * (max_spheres + 1))   # Add 1 since random does not include 1
        n_spheres = max_spheres
        i = 0   # Counter for our while loop. Will only increment if we can add a hypersphere.
        shuffled_data = np.copy(self.data)
        random.shuffle(shuffled_data)

        while i < n_spheres:
            for item in shuffled_data:
                found_something = False
                radius = np.random.random() * (max_radius - min_radius) + min_radius
                point = item
                # Create a random hypersphere
                if not self.does_sphere_intersect(point, radius):
                    self.remove_sphere(point, radius)
                    sphere = [point, radius]
                    self.spheres.append(sphere)
                    i = i + 1
                    found_something = True
                    print(i,'/',n_spheres,'Removing sphere with center point', sphere, 'with radius', radius)
                    if i >= n_spheres:
                        break
            if not found_something:
                print('Couldn\'t place that many holes!', i,'/',n_spheres)
                break

    # torus: you need a line segment, a minimum and max distance from the line 
    # bottom and top of line segment: make a line and anything greater than the line is out
    # otherwise it's within the line - how far is the shortest distance from the line to the point?
    # three dimensions: a plane with max and min distance from the plane? if we cut off the plane, we just get a sphere surface?
    def remove_torus(self, point, direction, min_radius, max_radius, height):
        indices = []
        for index,item in enumerate(self.data):
            # find the position of the point on the line closest to this point
            t = find_t(point, direction, item) 
            # make sure it's not too far up/down. we don't want the torus continuing along the whole line, only a segment
            if abs(t) < height/2 : 
                # find the closest point on the line to this point
                q = point + t * direction
                # Get the shortest distance between this point and the line
                distance = distanceXd(q, item)
                if (distance <= max_radius) and (distance >= min_radius):
                    indices.append(index)
        self.data = np.delete(self.data, indices, 0)

    # return the point cloud - for printing
    def get_data(self):
        return self.data

# parametric line a + td and point p. line_point is a, direction is d, point is p.
# we want the closest point on the line to the point 
def find_t(line_point, direction, point):
    acc_top = 0
    acc_bottom = 0
    for a,d,p in zip(line_point, direction, point):
        acc_top += p * d
        acc_top -= a * d
        acc_bottom += math.pow(d,2)
    return acc_top / acc_bottom
