import math
import numpy as np
import random
import yaml

from Geometry import intersect_or_touch, rotate_grid
from Shape import Shape


class Spheroid(Shape):
    # full_grid:    all other objects
    # center:       center of the sphere
    # radius:       radius of the sphere
    def __init__(self, full_grid, center, radius, rotation):
        # Check we're not starting in an invalid location
        if intersect_or_touch(center, full_grid):
            self.valid = False
            return

        # Set sphere information
        self.center = [32,32,32]
        self.radius = radius
        self.full_grid = full_grid
        self.rotation = rotation
        self.valid = True

        size = full_grid[0][0].size
        self.x, self.y, self.z = rotate_grid(size, self.rotation, self.center)

        self._place()

        self.draw_grid = self.grid

    # Make a random spheroid
    @classmethod
    def random(cls, grid, shape_config, random_walk_config):
        # Read values from config file
        with open(shape_config, "r") as stream:
            data_loaded = yaml.safe_load(stream)
        center_place = data_loaded["Spheroid"]["center_placement_border"]
        min_radius = data_loaded["Spheroid"]["min_radius"]
        max_radius = data_loaded["Spheroid"]["max_radius"]
        size = grid[0][0].size

        # Create a spheroid randomly
        center = (
            random.randrange(center_place, size - center_place, 1),
            random.randrange(center_place, size - center_place, 1),
            random.randrange(center_place, size - center_place, 1),
        )
        if min_radius == max_radius:
            radius = [min_radius, min_radius, min_radius]
        else:
            radius = [
                random.randrange(min_radius, max_radius, 1),
                random.randrange(min_radius, max_radius, 1),
                random.randrange(min_radius, max_radius, 1),
            ]
        rotation = [
            random.uniform(0, 2 * math.pi),
            random.uniform(0, 2 * math.pi),
            random.uniform(0, 2 * math.pi),
        ]
        return cls(grid, center, radius, rotation)

    def _create_grid(self):
        # Create a spheroid
        self.grid = (
            (pow(self.x - self.center[0], 2) / pow(self.radius[0], 2))
            + (pow(self.y - self.center[1], 2) / pow(self.radius[1], 2))
            + (pow(self.z - self.center[2], 2) / pow(self.radius[2], 2))
        ) <= 1

    # This only gets called if it's not surrounded - there's no other things to check for a ball
    def _valid_edge(self, point):
        return True
