import numpy as np
import random

from Objects import Sphere

# Class that holds one object with cavities in it, of various shapes.
class HyperCube(object):
    # Constructor
    def __init__(self, size):
        self.size = size # we are making a cube so this is the number of voxels across any edge
        self.objects = [] # initialise our list of objects
        # Create the full shape everything is contained in. True areas are the border and false are the insides
        x, y, z, w = np.indices((self.size, self.size, self.size, self.size))
        self.border = (x == 0) | (x == self.size - 1) | (y == 0) | (y == self.size - 1) | (z == 0) | (z == self.size - 1) | (w == 0) | (w == self.size - 1)  # lets use a hypercube

    # num_objects is a dictionary with numbers of each object
    def add_objects(self, num_objects):
        for key in num_objects:
            if key == "sphere":
                for _ in range(num_objects[key]):
                    while(not self.add_object(Sphere.random(self.get_objects(), self.size))):
                        continue

    # Check if this object intersects or touches any others, if not we can add it to the list
    def add_object(self, object):
        if object.valid:
            self.objects.append(object)
            return True
        return False
 
     # Given an object, check if it intersects with existing objects
    def check_intersect(self, new_object):
        if (new_object & self.border).any():
            return True
        
        for object in self.objects:
            if (object.grid & new_object).any():
                return True
        return False

    # Get all the 'holes' as solid objects
    def get_objects(self):
        # Make a full false grid
        x, y, z, w = np.indices((self.size, self.size, self.size, self.size))
        grid = x + y + z + w < 0
        # Loop over all objects and add them to the voxel grid 
        for object in self.objects:
            grid = grid | object.grid

        return grid

    # Get the full cube with holes
    def get_full_objects(self):
        return ~self.get_objects()

    # Return betti numbers of the full object
    def get_data(self):
        sphere_count = 0
        torus_count = 0
        torus2_count = 0
        island_count = 0
        tunnel_count = 0
        # Loop over all objects and add their betti numbers
        for object in self.objects:
            if isinstance(object, Sphere):
                sphere_count += 1
        # Return a dictionary of the numbers to go into a yaml file
        return [{"sphere": sphere_count}, 
            {"torus": torus_count},
            {"2torus": torus2_count}, 
            {"island": island_count},
            {"tunnel": tunnel_count}]
            