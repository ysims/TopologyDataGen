import numpy as np
import random
import scipy.ndimage
import itertools
import sys

sys.path.append("Objects")

from Island import Island
from Octopus import Octopus
from Spheroid import Spheroid
from Torus import Torus, TorusN
from Tunnel import Tunnel

# Class that holds a cube with cavities in it,
# of various configurations
class BettiCube(object):
    def __init__(self, size, shape_config, random_walk_config, torus_holes):
        # The number of voxels across any edge
        self.shape_config = shape_config
        self.random_walk_config = random_walk_config
        self.size = size
        self.torus_holes = torus_holes
        self.objects = []  # initialise our list of objects
        # Create the full shape everything is contained in.
        # True areas are the border and false are the insides
        x, y, z = np.indices((self.size, self.size, self.size))
        self.border = (
            (x == 0)
            | (x == self.size - 1)
            | (y == 0)
            | (y == self.size - 1)
            | (z == 0)
            | (z == self.size - 1)
        )

    # Add the specified objects from the dictionary
    # to the cube as cavities
    # num_objects is a dictionary
    #   key is the name of an object class
    #   value is the number of that object to generate
    def add_objects(self, num_objects):
        for key in num_objects:
            for _ in range(num_objects[key]):
                if key == "Octopus Spheroid":
                    while not self.add_object(Octopus.random(self.get_objects(draw=False), self.shape_config, self.random_walk_config, "Spheroid")):
                        continue
                elif key == "Octopus Torus":
                    while not self.add_object(Octopus.random(self.get_objects(draw=False), self.shape_config, self.random_walk_config, "Torus")):
                        continue
                elif key == "Octopus Torus2":
                    while not self.add_object(Octopus.random(self.get_objects(draw=False), self.shape_config, self.random_walk_config, "Torus2")):
                        continue
                elif key == "Octopus Torus3":
                    while not self.add_object(Octopus.random(self.get_objects(draw=False), self.shape_config, self.random_walk_config, "Torus3")):
                        continue

                elif key == "TorusN":
                    while not self.add_object(
                        eval(
                            key
                            + ".random(self.get_objects(draw=False), self.shape_config, self.random_walk_config, self.torus_holes)"
                        )
                    ):
                        continue
                else:
                    while not self.add_object(
                        eval(
                            key
                            + ".random(self.get_objects(draw=False), self.shape_config, self.random_walk_config)"
                        )
                    ):
                        continue

        # for object in self.objects:
        #     if isinstance(object, Octopus):
        #         object.addTentacles(self.get_objects(draw=False))

    # Adds a random object to the cube
    # from a set of allowed objects
    def add_random(self):
        objects = ["Tunnel", "Torus", "TorusN", "Spheroid", "Island", "Octopus"]

        # Loop until object is successfully added
        while not self.add_object(
            eval(
                objects[random.randrange(0, len(objects), 1)]
                + ".random(self.get_objects(draw=False))"
            )
        ):
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
        x, _, _ = np.indices((self.size, self.size, self.size))
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

    # Returns a point cloud with 4d vectors, the 4th dimension corresponds to the object it represents
    def get_separate_objects(self):
        numpy_point_cloud = None
        for index, object in enumerate(self.objects):
            for X, Y, Z in itertools.product(range(0, self.size), repeat=3):
                if object.grid[X][Y][Z]:
                    if type(numpy_point_cloud) is np.ndarray:
                        numpy_point_cloud = np.concatenate(
                            (numpy_point_cloud, [[X, Y, Z, index]]), axis=0
                        )
                    else:
                        numpy_point_cloud = np.array([[X, Y, Z, index]])
        return numpy_point_cloud


    # Return count of all objects
    def get_data(self):
        spheroid_count = 0
        torus_count = 0
        torusN_count = 0
        island_count = 0
        tunnel_count = 0
        octopus_count = 0

        # Loop over all objects and add their betti numbers
        for object in self.objects:
            if isinstance(object, Spheroid):
                spheroid_count += 1
            elif isinstance(object, Torus):
                torus_count += 1
            elif isinstance(object, TorusN):
                torusN_count += 1
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
            "TorusN": torusN_count,
            "Island": island_count,
            "Tunnel": tunnel_count,
            "Octopus": octopus_count,
        }

    def get_octopus_data(self):
        obj = {"spheroid": 0, "torus": 0, "torus2": 0, "torus3": 0}

        # Loop over all objects and add their betti numbers
        for object in self.objects:
            if object.shape_name == "Spheroid":
                obj["spheroid"] += 1
            elif object.shape_name == "Torus":
                obj["torus"] += 1
            elif object.shape_name == "Torus2":
                obj["torus2"] += 1
            elif object.shape_name == "Torus3":
                obj["torus3"] += 1

        # Return a dictionary of the numbers to go into a yaml file
        return obj