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
    def __init__(self, full_grid, center, radius, rotation, object_min_distance, dimensions):
        # Check we're not starting in an invalid location
        if intersect_or_touch(center, full_grid, object_min_distance):
            self.valid = False
            return

        # Set sphere information
        self.center = center
        self.radius = radius
        self.full_grid = full_grid
        self.rotation = rotation
        self.valid = True
        self.dimensions = dimensions

        grid_size = full_grid
        for _ in range(dimensions - 1):
            grid_size = grid_size[0]
        grid_size = grid_size.size
        self.index_grid = rotate_grid(grid_size, self.rotation, self.center)

        self._place(object_min_distance)

        self.draw_grid = self.grid

    # Make a random spheroid
    @classmethod
    def random(cls, grid, shape_config, random_walk_config, dimensions):
        # Read values from config file
        with open(shape_config, "r") as stream:
            data_loaded = yaml.safe_load(stream)
        center_place = data_loaded["Spheroid"]["center_placement_border"]
        min_radius = data_loaded["Spheroid"]["min_radius"]
        max_radius = data_loaded["Spheroid"]["max_radius"]
        object_min_distance = data_loaded["object_min_distance"]

        grid_size = grid
        for _ in range(dimensions-1):
            grid_size = grid_size[0]
        grid_size = grid_size.size

        # Create a spheroid randomly
        center = [
            random.randrange(center_place, grid_size - center_place, 1) for _ in range(dimensions)
        ]
        if min_radius == max_radius:
            radius = [min_radius for _ in range(dimensions)]
        else:
            radius = [
                random.randrange(min_radius, max_radius, 1) for _ in range(dimensions)
            ]
        rotation = [
            random.uniform(0, 2 * math.pi) for _ in range(dimensions)
        ]
        return cls(grid, center, radius, rotation, object_min_distance, dimensions)

    def _create_grid(self):
        # Create a spheroid
        for i in range(self.dimensions):
            if i == 0:
                lhs = (pow(self.index_grid[i] - self.center[i], 2) / pow(self.radius[i], 2))
                continue
            lhs += (pow(self.index_grid[i] - self.center[i], 2) / pow(self.radius[i], 2))

        self.grid = lhs <= 1

    # This only gets called if it's not surrounded - there's no other things to check for a ball
    def _valid_edge(self, point):
        return True
