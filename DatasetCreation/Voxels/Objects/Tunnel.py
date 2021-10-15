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

    def _try_add(self, direction, all_points):
        pass
        # Don't repeat ourselves
        # if all_points.count(new_point) > 0:
        #     return False

        # # We don't want to intersect or touch the rest of the tunnel
        # if intersect_or_touch(new_point, self.grid):
        #     return False

        # It is ok if it's on the boundary
        # We need to allow this otherwise
        # the stop condition will never be satified
        # for x in new_point:
        #     if x == self.full_grid[0][0].size - 1 or x == 0:
        #         return True

        # Cannot intersect or touch the rest of the grid
        # But ignore the boundary when checking this since
        # We want to hit the boundary
        # if obj_intersect_touch(new_point, self.full_grid):
        #     return False
        # return True

    # Determines a start location for the walk
    # and returns the first point in the walk
    def _get_start(self):
        pass

    def _add_last_points(self, last_point, all_points):
        border = [
            [0, 1],
            [-1, 0],
            [1, 0],
            [0, -1],
            [-1, -1],
            [-1, 1],
            [1, 1],
            [1, -1],
        ]
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
        for border in add_border:
            try:  # skip if this is out of bounds
                add_point = [
                    last_point[0] + border[0],
                    last_point[1] + border[1],
                    last_point[2] + border[2],
                ]
                all_points[len(all_points) - 1].append(add_point)
            except:
                pass

    # Stop if we're on the boundary
    def _stop_walk_condition(self, all_points):
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
        return True

    # Not implemented
    # Branching tunnels not supported
    def _branch_start(self, _path):
        pass

    # Not implemented
    # Branching tunnels not supported
    def _num_branches(self, path):
        pass
