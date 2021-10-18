import math
import numpy as np
import random
import yaml

from Geometry import distance3d
from Shape import Shape


# This object represents a sphere with a sphere-shaped hole inside it
class Island(Shape):
    # center: center of the island
    # outer radius: radius of the outer sphere
    # inner radius: radius of the inner sphere
    # rotation: a list of three rotations that are x,y,z axis
    #           rotations and rotated in that order
    def __init__(self, full_grid, center, outer_radius, inner_radius, rotation):
        # Set sphere information
        self.full_grid = full_grid
        self.center = center
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.rotation = rotation
        self.valid = True

        # Find a center that works
        self._place()

        # Make a rotated grid and use it to make a voxelised sphere
        # with a hole in the middle (island)
        size = full_grid[0][0].size
        x, y, z = np.indices((size, size, size))
        self.draw_grid = (
            (pow(x - center[0], 2) + pow(y - center[1], 2) + pow(z - center[2], 2))
            <= outer_radius ** 2
        ) & (
            (pow(x - center[0], 2) + pow(y - center[1], 2) + pow(z - center[2], 2))
            >= inner_radius ** 2
        )
        # Set self.grid
        self._create_grid()

    # Make a random island
    @classmethod
    def random(cls, grid, shape_config, random_walk_config):
        # Read values from config file
        with open(shape_config, "r") as stream:
            data_loaded = yaml.safe_load(stream)
        center_place = data_loaded["Island"]["center_placement_border"]
        min_outer = data_loaded["Island"]["min_outer_radius"]
        max_outer = data_loaded["Island"]["max_outer_radius"]
        min_inner = data_loaded["Island"]["min_inner_radius"]
        size = grid[0][0].size

        # Make random Island
        rotation = [
            random.uniform(0, 2 * math.pi),
            random.uniform(0, 2 * math.pi),
            random.uniform(0, 2 * math.pi),
        ]
        center = [
            random.randrange(center_place, size - center_place, 1),
            random.randrange(center_place, size - center_place, 1),
            random.randrange(center_place, size - center_place, 1),
        ]
        if min_outer == max_outer:
            outer_radius = min_outer
        else:
            outer_radius = random.randrange(min_outer, max_outer, 1)
        if min_inner == outer_radius:
            inner_radius = min_inner
        else:
            inner_radius = random.randrange(min_inner, outer_radius - 1, 1)
        return cls(grid, center, outer_radius, inner_radius, rotation)

    # Make this as a ball for finding a good center,
    # or we might trap an object inside...
    def _create_grid(self):
        # Create a sphere
        size = self.full_grid[0][0].size
        x, y, z = np.indices((size, size, size))
        self.grid = (
            pow(x - self.center[0], 2)
            + pow(y - self.center[1], 2)
            + pow(z - self.center[2], 2)
        ) <= pow(self.outer_radius, 2)

    # Only valid if it's not in the inside cavity
    def _valid_edge(self, point):
        if distance3d(point, self.center) <= self.inner_radius:
            return False
        return True
