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
        self.width = 2

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
        next_point = list(map(add, direction, all_points[len(all_points) - 1][0]))
        if obj_intersect_touch(next_point, (self.grid | self.full_grid), True):
            return False
        # Don't repeat a point we've already done
        for points in all_points:
            if next_point == points[0]:
                return False
        points_to_be_added = [next_point]
        border = [[0, 1], [1, 0], [1, 1]]
        add_border = (
            [[0, b[0], b[1]] for b in border]
            if direction[0] != 0
            else [[b[0], 0, b[1]] for b in border]
            if direction[1] != 0
            else [[b[0], b[1], 0] for b in border]
        )
        for border in add_border:
            try:  # skip if this is out of bounds
                test_point = [
                    next_point[0] + border[0],
                    next_point[1] + border[1],
                    next_point[2] + border[2],
                ]
                if not obj_intersect_touch(test_point, (self.grid | self.full_grid)):
                    points_to_be_added.append(test_point)
                else:
                    return False
            except:
                pass

        all_points.append(points_to_be_added)

        if len(all_points) > 2:
            last_index = len(all_points) - 2
            for i in range(0, last_index + 1):
                for point in all_points[i]:
                    self.grid[point[0]][point[1]][point[2]] = True

        # count = 0
        # for points in all_points:
        #     if self.grid[points[0][0]][points[0][1]][points[0][2]] == True:
        #         print("point", count, "is in")
        #         for point in points:
        #             if self.grid[point[0]][point[1]][point[2]] != True:
        #                 print("the thing is true but the surrounding is not")
        #     else:
        #         print("point", count, "is not in")
        #     count += 1

        return True

    # Get the vector to add to a point to give it a border thickness
    def _get_border(self):
        border = [[0, 1], [1, 0], [1, 1]]
        return (
            [[0, b[0], b[1]] for b in border]
            if self.start[0] == 0 or self.start[0] == self.full_grid[0][0].size - 1
            else [[b[0], 0, b[1]] for b in border]
            if self.start[1] == 0 or self.start[1] == self.full_grid[0][0].size - 1
            else [[b[0], b[1], 0] for b in border]
        )

    # Determines a start location for the walk
    # and returns the first point in the walk
    def _get_start(self):
        all_points = []
        # Fill out the starting point
        if not self._get_first_points(all_points):
            return []
        # For each thickness in the width,
        # add an extra point straight on from the starting point
        # to prevent
        for _ in range(self.width):
            if not self._get_next_point(all_points):
                return []
        return all_points

    # Try to add a border around the starting point
    def _get_first_points(self, all_points):
        if obj_intersect_touch(self.start, self.full_grid):
            return False
        points_to_be_added = [self.start]
        add_border = self._get_border()
        for border in add_border:
            try:  # skip if this is out of bounds
                test_point = [
                    self.start[0] + border[0],
                    self.start[1] + border[1],
                    self.start[2] + border[2],
                ]
                if not obj_intersect_touch(test_point, self.full_grid):
                    points_to_be_added.append(test_point)
                else:
                    return False
            except:
                pass
        all_points.append(points_to_be_added)
        return True

    # Try to add another point after the starting point/s
    def _get_next_point(self, all_points):
        # Create a new point facing forwards (start point perspective)
        forward_direction = [
            1 if x is 0 else -1 if x is (self.grid[0][0].size) - 1 else 0
            for x in self.start
        ]
        next_point = list(
            map(add, forward_direction, all_points[len(all_points) - 1][0])
        )
        # Check if the point is valid
        if obj_intersect_touch(next_point, self.full_grid):
            return []
        points_to_be_added = [next_point]
        # Get the border and try to add the points
        add_border = self._get_border()
        for border in add_border:
            try:  # skip if this is out of bounds
                test_point = [
                    next_point[0] + border[0],
                    next_point[1] + border[1],
                    next_point[2] + border[2],
                ]
                if not obj_intersect_touch(test_point, self.full_grid):
                    points_to_be_added.append(test_point)
                else:
                    return False
            except:
                pass
        all_points.append(points_to_be_added)
        return True

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
        # if len(all_points) > 6:
        #     # for points in all_points:
        #     #     for point in points:
        #     #         if self.grid[point[0]][point[1]][point[2]]:
        #     #             pass
        #     #             # print(point, "is in the grid")
        #     print("It's a tunnel! \n", all_points)
        #     return True
        last_points = all_points[len(all_points) - 1]
        for last_point in last_points:
            for x in last_point:
                if x == self.full_grid[0][0].size - 1 or x == 0:
                    # self._add_last_points(last_point, all_points)
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
