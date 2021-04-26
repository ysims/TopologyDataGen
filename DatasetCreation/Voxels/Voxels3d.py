import numpy as np
import random
import scipy.ndimage

from Objects import Sphere,Torus,Island,Line

# Class that holds one object with cavities in it, of various shapes.
class Voxels3d(object):
    # Constructor
    def __init__(self, size):
        self.size = size # we are making a cube so this is the number of voxels across any edge
        self.objects = [] # initialise our list of objects
        # Create the full shape everything is contained in. True areas are the border and false are the insides
        x, y, z = np.indices((self.size, self.size, self.size))
        self.border = (x == 0) | (x == self.size - 1) | (y == 0) | (y == self.size - 1) | (z == 0) | (z == self.size - 1) # lets use a cube

    # Add num_object number of objects randomly
    def add_objects(self, num_objects, num_lines):
        count = 0
        exit_count = 0
        while (count < num_objects) and (exit_count < 20): 
            if(self.add_random()):
                # print("Success!")
                count += 1
                exit_count = 0
            else:
                exit_count += 1
        if (exit_count > 20):
            print("Exit count!!!")
        count = 0
        exit_count = 0
        while (count < num_lines) and (exit_count < 20):
            new_line = Line.random(self.size, self.get_objects(), self.border)
            if(new_line.valid):
                self.objects.append(new_line)
                count += 1
                exit_count = 0
            else:
                exit_count += 1
        if (exit_count > 20):
            print("Exit count!!!")

    def add_random(self):
        # We're gonna choose a shape randomly. There are three at the moment, so lets get [0-1] randomly
        shape = random.randrange(0, 3, 1)
        # Sphere
        if shape == 0:
            # print("Sphere")
            return self.add_object(Sphere.random(self.size))
        elif shape == 1:
            # print("Island")
            return self.add_object(Island.random(self.size))
        else:
            # print("Torus")
            return self.add_object(Torus.random(self.size))

    # Check if this object intersects or touches any others, if not we can add it to the list
    def add_object(self, object):
        object_dilation = scipy.ndimage.binary_dilation(object.grid,iterations=2)
        if self.check_intersect(object_dilation):
            return False
        self.objects.append(object)
        return True
 
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
        x, y, z = np.indices((self.size, self.size, self.size))
        grid = x + y + z < 0
        # Loop over all objects and add them to the voxel grid 
        for object in self.objects:
            grid = grid | object.grid
        return grid

    # Get the full cube with holes
    def get_full_objects(self):
        return ~self.get_objects()

    # Return betti numbers of the full object
    def get_betti(self):
        betti_zero = 1  # the cube is one connected component
        betti_one = 0
        betti_two = 0
        # Loop over all objects and add their betti numbers
        for object in self.objects:
            betti_zero += object.betti_zero
            betti_one += object.betti_one
            betti_two += object.betti_two
        # Return a dictionary of the numbers to go into a yaml file
        return [{"betti_zero": betti_zero}, 
            {"betti_one": betti_one}, 
            {"betti_two": betti_two}]