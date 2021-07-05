import numpy as np
import random
import scipy.ndimage

from Objects import Sphere,Torus,Torus2,Island,Tunnel

# Class that holds one object with cavities in it, of various shapes.
class BettiCube(object):
    # Constructor
    def __init__(self, size):
        self.size = size # we are making a cube so this is the number of voxels across any edge
        self.objects = [] # initialise our list of objects
        # Create the full shape everything is contained in. True areas are the border and false are the insides
        x, y, z = np.indices((self.size, self.size, self.size))
        self.border = (x == 0) | (x == self.size - 1) | (y == 0) | (y == self.size - 1) | (z == 0) | (z == self.size - 1) # lets use a cube

    # num_objects is a dictionary with numbers of each object
    def add_objects(self, num_objects):
        for key in num_objects:
            if key == "tunnel":
                for _ in range(num_objects[key]):
                    while(not self.add_object(Tunnel.random(self.size, self.get_objects(draw=False), self.border))):
                        continue
            
            if key == "torus":
                for _ in range(num_objects[key]):
                    while(not self.add_object(Torus.random(self.size))):
                        continue
            
            if key == "torus2":
                for _ in range(num_objects[key]):
                    while(not self.add_object(Torus2.random(self.size))):
                        continue
                
            if key == "sphere":
                for _ in range(num_objects[key]):
                    while(not self.add_object(Sphere.random(self.get_objects(draw=False), self.size))):
                        continue

            if key == "island":
                for _ in range(num_objects[key]):
                    while(not self.add_object(Island.random(self.size))):
                        continue
        

    def add_random(self):
        # We're gonna choose a shape randomly. There are three at the moment, so lets get [0-1] randomly
        shape = random.randrange(0, 4, 1)
        # Sphere
        if shape == 0:
            return self.add_object(Sphere.random(self.get_objects(draw=False), self.size))
        elif shape == 1:
            return self.add_object(Island.random(self.size))
        elif shape == 2:
            return self.add_object(Torus2.random(self.size))
        else:
            return self.add_object(Torus.random(self.size))

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
    def get_objects(self, draw):
        # Make a full false grid
        x, y, z = np.indices((self.size, self.size, self.size))
        grid = x + y + z < 0
        # Loop over all objects and add them to the voxel grid 
        for object in self.objects:
            grid = grid | object.grid
            # Get the disc that 'plugs' up the torus so we don't link
            if isinstance(object, Torus) & (not draw):
                grid = grid | object.get_disc()
        # Add the border to it if we're not drawing
        if not draw:
            grid = grid | self.border
        return grid

    # Get the full cube with holes
    def get_full_objects(self):
        return ~self.get_objects(draw=True)

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
            if isinstance(object, Torus):
                torus_count += 1
            if isinstance(object, Torus2):
                torus2_count += 1
            if isinstance(object, Island):
                island_count += 1
            if isinstance(object, Tunnel):
                tunnel_count += 1
        # Return a dictionary of the numbers to go into a yaml file
        return [{"sphere": sphere_count}, 
            {"torus": torus_count},
            {"2torus": torus2_count}, 
            {"island": island_count},
            {"tunnel": tunnel_count}]
            