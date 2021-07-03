import numpy as np
import itertools
import random
import math
from operator import add

from Geometry import distance4d, intersect_or_touch

class Sphere(object): 

    # center: center of the sphere
    # radius: radius of the sphere
    # size: how big the voxel grid is
    def __init__(self, full_grid, center, radius, size):
        # Check we're not starting in an invalid location
        if intersect_or_touch(center, full_grid):
            self.valid = False
            return

        # Set sphere information
        self.center = center
        self.radius = radius
        self.true_radius = 0
        self.full_grid = full_grid
        self.valid = True
        self.size = size
        
        self.create_sphere()

        # If the sphere wasn't possible to make without it being very small, don't use it
        if self.true_radius < 3:
            self.valid = False

    # Make a random sphere
    @classmethod
    def random(cls, grid, size):
        center = (random.randrange(1, size-1, 1), random.randrange(1, size-1, 1), random.randrange(1, size-1, 1), random.randrange(1, size-1, 1))
        radius = random.randrange(3, int(size/6), 1)
        return cls(grid, center, radius, size)

    # Creates a sphere by starting at the center and spreading out to adjacent voxels and adding them to the grid if they pass certain checks.
    # The checks involve not touching or intersecting another object and not exceeding the requested radius of the sphere.
    def create_sphere(self):
        # Create a sphere as best we can with these parameters
        x, y, z, w = np.indices((self.size, self.size, self.size, self.size))
        self.grid = (x > self.size)   # False grid
        
        # Add all possible movement directions
        movement_direction = [] # list of value movements
        for x,y,z,w in itertools.permutations([1,0,0,0],4):
            movement_direction.append((x,y,z,w))
            movement_direction.append((-x,-y,-z,-w))
        movement_direction.sort()
        movement_direction = list(movement_direction for movement_direction,_ in itertools.groupby(movement_direction)) # remove duplicates

        # Create the set that will store the points we need to check
        point_set = {self.center}

        while (len(point_set) > 0):
            # print(len(point_set))
            point = point_set.pop()
            # print(point)
            try:    # skip if this is out of bounds

                # THROWOUTS
                # We don't want to do anything with this point if we've already done it before
                if self.grid[point[0]][point[1]][point[2]][point[3]]:
                    continue
                
                # Check that we've not exceeded the requested radius of the sphere
                if distance4d(self.center, point) > self.radius:
                    continue

                # Make sure this doesn't intersect or touch something
                if intersect_or_touch(point, self.full_grid):
                    continue
                
                # KEEP
                # Add the point and add neighbours to the set if it passes the tests
                self.grid[point[0]][point[1]][point[2]][point[3]] = True
                
                # Update the distance if needed
                if self.true_radius < distance4d(self.center, point):
                    self.true_radius = distance4d(self.center, point)
                
                for movement in movement_direction:
                    point_set.add((point[0] + movement[0], point[1] + movement[1], point[2] + movement[2], point[3] + movement[3]))

            except:     # Continue to the next one
                continue
