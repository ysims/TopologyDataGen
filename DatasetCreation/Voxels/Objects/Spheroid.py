import numpy as np
import random
import yaml

from Geometry import intersect_or_touch
from Shape import Shape


class Spheroid(Shape):
    # full_grid:    all other objects
    # center:       center of the sphere
    # radius:       radius of the sphere
    def __init__(self, full_grid, center, radius):
        # Check we're not starting in an invalid location
        if intersect_or_touch(center, full_grid):
            self.valid = False
            return

        # Set sphere information
        self.center = center
        self.radius = radius
        self.full_grid = full_grid
        self.valid = True

        self._place_and_move()
        
    # Make a random spheroid
    @classmethod
    def random(cls, grid):
        # Read values from config file
        with open("./Objects/Shape.yaml", 'r') as stream:
            data_loaded = yaml.safe_load(stream)
        center_place = data_loaded["Spheroid"]["center_placement_border"]
        min_radius = data_loaded["Spheroid"]["min_radius"]
        max_radius = data_loaded["Spheroid"]["max_radius"]
        size = grid[0][0].size

        # Create a spheroid randomly
        center = (random.randrange(center_place, size-center_place, 1), 
            random.randrange(center_place, size-center_place, 1), 
            random.randrange(center_place, size-center_place, 1))
        radius = [random.randrange(min_radius, max_radius, 1), 
            random.randrange(min_radius, max_radius, 1), 
            random.randrange(min_radius, max_radius, 1)]
        return cls(grid, center, radius)

    def _create_grid(self):
        # Create a spheroid
        size = self.full_grid[0][0].size
        x,y,z = np.indices((size, size, size))
        self.grid = ((pow(x - self.center[0],2) / pow(self.radius[0],2))
            + (pow(y - self.center[1],2) / pow(self.radius[1],2))
            + (pow(z - self.center[2], 2) / pow(self.radius[2],2))) <= 1

    # This only gets called if it's not surrounded - there's no other things to check for a ball
    def _valid_edge(self, point):
        return True
