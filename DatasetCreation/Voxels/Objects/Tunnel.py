import numpy as np
from operator import add
import random

from Geometry import intersect_or_touch, obj_intersect_touch
from RandomWalk import RandomWalk


class Tunnel(RandomWalk):
    # Parameters
    # start: coordinate where the tunnel starts
    # objects: list of objects for the tunnel to avoid
    # Description
    # Given a starting position on the border, make a tunnel from this point to some other point on the border
    # Any border point should not intersect with an object since object cannot be on the border
    def __init__(self, full_grid, start):
        # Set tunnel information
        self.full_grid = full_grid
        self.start = start
        # Don't worry about branching rn, we might not care about tunnels
        # And branching might be too complex to count
        self.branching = False

        # Make a grid with just this starting point
        size = self.full_grid[0][0].size
        x, y, z = np.indices((size, size, size))
        self.grid = x > size  # False grid

        self.valid = self._random_walk()

        self.draw_grid = self.grid

    # Make a random tunnel
    @classmethod
    def random(cls, full_grid):
        size = full_grid[0][0].size
        # Create a random start position on a face
        start = [random.randrange(2, size - 2, 1) for _ in range(0, 3)]
        start[random.randrange(0, 3, 1)] = (
            0 if random.randrange(0, 2, 1) == 0 else size - 1
        )
        return cls(full_grid, start)

    def _allowed_point(self, new_point, all_points):
        # Don't repeat ourselves
        if all_points.count(new_point) > 0:
            return False

        # We don't want to intersect or touch the rest of the tunnel
        if intersect_or_touch(new_point, self.grid):
            return False

        # It is ok if it's on the boundary
        # We need to allow this otherwise
        # the stop condition will never be satified
        for x in new_point:
            if x == self.full_grid[0][0].size - 1 or x == 0:
                return True

        # Cannot intersect or touch the rest of the grid
        # But ignore the boundary when checking this since
        # We want to hit the boundary
        if obj_intersect_touch(new_point, self.full_grid):
            return False
        return True

    # Determines a start location for the walk
    # and returns the first point in the walk
    def _get_start(self):
        all_points = []
        all_points.append(self.start)
        if obj_intersect_touch(self.start, self.full_grid):
            return []

        # Find the forward direction
        size = self.grid[0][0].size
        forward = [1 if x is 0 else -1 if x is size - 1 else 0 for x in self.start]
        second_point = list(map(add, forward, self.start))
        if obj_intersect_touch(second_point, self.full_grid):
            return []
        all_points.append(second_point)
        return all_points

    # Stop if we're on the boundary
    def _stop_walk_condition(self, all_points):
        last_point = all_points[len(all_points) - 1]
        for x in last_point:
            if x == self.full_grid[0][0].size - 1 or x == 0:
                return True
        return False

    # If the tunnel didn't stop on the boundary, it's not valid
    # Only want tunnels that go from one boundary to another
    def _acceptable_walk(self, all_points):
        return True

    # Not implemented
    # Branching tunnels not supported
    def _branch_start(self, _path):
        pass

    # Not implemented
    # Branching tunnels not supported
    def _num_branches(self, path):
        pass
