import copy
import math
import numpy as np
from operator import add
import random
import yaml

from Geometry import obj_intersect_touch
from RandomWalk import RandomWalk


class Tunnel(RandomWalk):
    # Parameters
    # start: coordinate where the tunnel starts
    # objects: list of objects for the tunnel to avoid
    # Description
    # Given a starting position on the border, make a tunnel from this point to some other point on the border
    # Any border point should not intersect with an object since object cannot be on the border
    def __init__(self, full_grid, start, random_walk_config):
        # Set tunnel information
        self.full_grid = full_grid
        self.start = start
        self.isBranching = False

        with open(random_walk_config, "r") as stream:
            data_loaded = yaml.safe_load(stream)
        self.min_width = data_loaded["Tunnel"]["min_width"]
        self.max_width = data_loaded["Tunnel"]["max_width"]
        self.branching = data_loaded["Tunnel"]["branching"]
        self.min_branching_length = data_loaded["Tunnel"]["min_branching_length"]

        # Make a grid with just this starting point
        size = self.full_grid[0][0].size
        x, y, z = np.indices((size, size, size))
        self.grid = x > size  # False grid

        # Draw the random walk
        self.valid = self._random_walk()
        self.draw_grid = self.grid

    # Make a random tunnel
    @classmethod
    def random(cls, full_grid, shape_config, random_walk_config):
        # Create a random start position on a face
        size = full_grid[0][0].size
        with open(random_walk_config, "r") as stream:
            data_loaded = yaml.safe_load(stream)
        min_width = data_loaded["Tunnel"]["min_width"]
        # Don't want to touch the corners,
        # adjust based on minimum width so no voxels touch the corners
        start = [
            random.randrange(1 + min_width, size - 1 - min_width, 1)
            for _ in range(0, 3)
        ]
        start[random.randrange(0, 3, 1)] = (
            0 if random.randrange(0, 2, 1) == 0 else size - 1
        )
        return cls(full_grid, start, random_walk_config)

    # Returns True if the point touches any existing objects
    # in the grid, or itself, but NOT the border
    # Returns False otherwise
    def _grid_check(self, point, grid):
        return obj_intersect_touch(point, grid)

    # Determines a start location for the walk
    # and returns the first point in the walk
    def _get_start(self):
        all_points = []

        forward_direction = [
            1 if x is 0 else -1 if x is (self.grid[0][0].size) - 1 else 0
            for x in self.start
        ]
        first_points = [self.start]
        # Fill out the starting point
        if not self._add_point_and_border(
            first_points, forward_direction, self.min_width
        ):
            return []
        all_points.append(first_points)
        # For each thickness in the width,
        # add an extra point straight on from the starting point
        # to prevent
        for _ in range(self.max_width + 1):
            next_point = list(
                map(add, forward_direction, all_points[len(all_points) - 1][0])
            )
            next_points = [next_point]
            if not self._add_point_and_border(
                next_points, forward_direction, self.min_width
            ):
                return []
            all_points.append(next_points)
        return all_points

    # Once a point touches the border, this will make sure that the connection
    # with the border has enough thickness to satisfy the minimum width
    def _add_last_points(self, last_point, all_points):
        border = [[0, 1], [1, 0], [1, 1]]
        border_x = [[0, b[0], b[1]] for b in border]
        border_y = [[b[0], 0, b[1]] for b in border]
        border_z = [[b[0], b[1], 0] for b in border]
        add_border = (
            border_x
            if last_point[0] == 0 or last_point[0] == self.full_grid[0][0].size - 1
            else border_y
            if last_point[1] == 0 or last_point[1] == self.full_grid[0][0].size - 1
            else border_z
        )

        if len(all_points[len(all_points) - 1]) > 1:
            width = int(math.log(len(all_points[len(all_points) - 1]), 2))
        else:
            width = 1

        # Points to add a border to, starting with the spine
        recurse_border = [last_point]
        for _ in range(0, width - 1):
            new_recurse_border = []  # the next set of points to add the border to
            # Add the border points to expand the width
            for recurse_border_point in recurse_border:
                for border in add_border:
                    try:  # skip if this is out of bounds
                        # Point to try to add
                        test_point = [
                            recurse_border_point[0] + border[0],
                            recurse_border_point[1] + border[1],
                            recurse_border_point[2] + border[2],
                        ]
                        # Don't want to intersect/touch the grid
                        if not self._grid_check(
                            test_point, (self.grid | self.full_grid)
                        ):
                            # Don't add it if it's already there
                            if all_points[len(all_points) - 1].count(test_point) == 0:
                                all_points[len(all_points) - 1].append(test_point)
                                new_recurse_border.append(test_point)
                        else:
                            return False
                    except:
                        pass

    # Stop if it's on the boundary
    def _stop_walk_condition(self, all_points):
        if self.isBranching:
            if len(all_points) >= self.branching_length:
                return True
            return False
        last_points = all_points[len(all_points) - 1]
        for last_point in last_points:
            for x in last_point:
                if x == self.full_grid[0][0].size - 1 or x == 0:
                    self._add_last_points(last_point, all_points)
                    return True
        return False

    # If the tunnel didn't stop on the boundary, it's not valid
    # Only want tunnels that go from one boundary to another
    def _acceptable_walk(self, all_points):
        if self.isBranching:
            if len(all_points) >= self.min_branching_length:
                return True
            return False
        last_point = all_points[len(all_points) - 1]
        for point in last_point:
            if min(point) == 0 or max(point) == self.grid[0][0].size - 1:
                return True
        return False
