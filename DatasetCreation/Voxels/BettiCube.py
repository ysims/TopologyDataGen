import numpy as np
import random
import scipy.ndimage

import sys
sys.path.append('Objects')

from Island import Island
from Octopus import Octopus
from Spheroid import Spheroid
from Torus import Torus, TorusN
from Tunnel import Tunnel

# Class that holds a cube with cavities in it, 
# of various configurations
class BettiCube(object):

    def __init__(self, size):
        # The number of voxels across any edge
        self.size = size
        self.objects = [] # initialise our list of objects
        # Create the full shape everything is contained in. 
        # True areas are the border and false are the insides
        x, y, z = np.indices((self.size, self.size, self.size))
        self.border = ((x == 0) | (x == self.size - 1) 
            | (y == 0) | (y == self.size - 1) 
            | (z == 0) | (z == self.size - 1))

    # Add the specified objects from the dictionary
    # to the cube as cavities
    # num_objects is a dictionary
    #   key is the name of an object class
    #   value is the number of that object to generate
    def add_objects(self, num_objects):
        for key in num_objects:
            for _ in range(num_objects[key]):
                while(not self.add_object(eval(key 
                        + ".random(self.get_objects(draw=False))"))):
                    continue

    # Adds a random object to the cube
    # from a set of allowed objects
    def add_random(self):
        objects = ["Tunnel", "Torus", "Torus2", 
            "Spheroid", "Island", "Octopus"]

        # Loop until object is successfully added
        while not self.add_object(eval(
                        objects[random.randrange(0, len(objects), 1)]
                        + ".random(self.get_objects(draw=False))")):
            continue

    # Check if this object was made correctly, 
    # if so we can add it to the list
    # Requires object to have a `valid` boolean value
    def add_object(self, object):
        if object.valid:
            self.objects.append(object)
            return True
        return False

    # Returns a grid with all the 'holes' as solid objects
    def get_objects(self, draw):
        x,_,_ = np.indices((self.size, self.size, self.size))
        grid = x < 0
        
        # Loop over all objects and add them to the voxel grid 
        for object in self.objects:
            grid = (grid | object.grid) if not draw else (grid | object.draw_grid)

        # Add the border to it if we're not drawing
        if not draw:
            grid = grid | self.border
        
        return grid

    # Get the full cube with holes
    def get_full_objects(self):
        return ~self.get_objects(draw=True)

    # Return count of all objects
    def get_data(self):
        spheroid_count = 0
        torus_count = 0
        torus2_count = 0
        island_count = 0
        tunnel_count = 0
        octopus_count = 0

        # Loop over all objects and add their betti numbers
        for object in self.objects:
            if isinstance(object, Spheroid):
                spheroid_count += 1
            elif isinstance(object, Torus):
                torus_count += 1
            elif isinstance(object, Torus2):
                torus2_count += 1
            elif isinstance(object, Island):
                island_count += 1
            elif isinstance(object, Tunnel):
                tunnel_count += 1
            elif isinstance(object, Octopus):
                octopus_count += 1

        # Return a dictionary of the numbers to go into a yaml file
        return {
            "Spheroid": spheroid_count,
            "Torus": torus_count,
            "Torus2": torus2_count,
            "Island": island_count,
            "Tunnel": tunnel_count,
            "Octopus": octopus_count,
}
            