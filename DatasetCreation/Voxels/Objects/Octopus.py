import copy
import itertools
import math
from operator import add
import random
import yaml
import numpy as np

from Geometry import intersect_or_touch, hard_surrounded
from RandomWalk import RandomWalk
from Spheroid import Spheroid
from Torus import Torus, TorusN


class Octopus(RandomWalk):
    def __init__(self, full_grid, num_tentacles, random_walk_config, shape_config):
        self.full_grid = full_grid
        self.num_tentacles = num_tentacles
        self.valid = True

        # Read values from config file
        with open(random_walk_config, "r") as stream:
            data_loaded = yaml.safe_load(stream)
        self.min_tentacle_length = data_loaded["Octopus"]["min_tentacle_length"]
        self.max_tentacle_length = data_loaded["Octopus"]["max_tentacle_length"]
        self.branching = data_loaded["Octopus"]["branching"]
        self.length_between_branches = data_loaded["Octopus"]["length_between_branches"]
        self.shape_name = data_loaded["Octopus"]["shape"]
        self.min_width = data_loaded["Octopus"]["min_width"]
        self.max_width = data_loaded["Octopus"]["max_width"]

        if self.shape_name == "Spheroid":
            self.shape = Spheroid.random(full_grid, shape_config, random_walk_config)
            while not self.shape.valid:
                self.shape = Spheroid.random(
                    full_grid, shape_config, random_walk_config
                )
        elif self.shape_name == "Torus":
            self.shape = Torus.random(full_grid, shape_config, random_walk_config)
            while not self.shape.valid:
                self.shape = Torus.random(full_grid, shape_config, random_walk_config)
        elif self.shape_name == "TorusN":
            self.shape = TorusN.random(full_grid, shape_config, random_walk_config)
            while not self.shape.valid:
                self.shape = TorusN.random(full_grid, shape_config, random_walk_config)
        elif self.shape_name == "None":
            size = full_grid[0][0].size
            x, y, z = np.indices((size, size, size))
            self.grid = x < 0

        else:
            print("Error: {} not supported".format(self.shape_name))
            return

        if self.shape_name != "None":
            self.grid = copy.copy(self.shape.draw_grid)

    # Make a random tunnel
    @classmethod
    def random(cls, full_grid, shape_config, random_walk_config):
        # Read values from config file
        with open(random_walk_config, "r") as stream:
            data_loaded = yaml.safe_load(stream)
        min_num_tentacles = data_loaded["Octopus"]["min_num_tentacles"]
        max_num_tentacles = data_loaded["Octopus"]["max_num_tentacles"]

        num_tentacles = random.randrange(min_num_tentacles, max_num_tentacles, 1)
        return cls(full_grid, num_tentacles, random_walk_config, shape_config)

    # Separate function for adding the tentacles
    # Since it'd be better to add them all later
    # Since they're easier to add than big objects
    def addTentacles(self, full_grid):
        self.full_grid = full_grid & (~self.grid)

        max_tries = 1000
        count = 0
        # Add the number of tentacles that we want
        # Retry if it fails
        for i in range(self.num_tentacles):
            count = 1
            while not self._random_walk():
                count += 1
                if count == max_tries:
                    break
                continue

        self.draw_grid = self.grid

    # Returns True if the point touches any existing objects
    # in the grid, or itself, or the border
    # Returns False otherwise
    def _grid_check(self, point, grid):
        return intersect_or_touch(point, grid)

    # Determines a start location for the walk
    # and returns the first point in the walk
    def _get_start(self):
        # Determine length of the tentacle
        self.tentacle_length = random.randrange(
            self.min_tentacle_length, self.max_tentacle_length, 1
        )
        all_points = []

        if self.shape_name != "None":
            # We will make a 'tentacle' going off from one of the edges
            edges = []
            for X, Y, Z in itertools.product(
                range(0, self.full_grid[0][0].size), repeat=3
            ):
                if self.shape.draw_grid[X][Y][Z] and not hard_surrounded(
                    [X, Y, Z], self.grid
                ):
                    edges.append([X, Y, Z])

            if not edges:
                print("No edges, something is wrong")
                self.valid = False
                return []
        else:
            # Edges could be any of the 'interior' points
            edges = []
            edges.append([15, 15, 15])

        # Grab a random edge to use
        # Don't add it to the path because it's already on the circle
        # Find one open spot to add to the path
        found_point = False
        directions = [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [-1, 0, 0],
            [0, -1, 0],
            [0, 0, -1],
        ]
        while not found_point:
            if not edges:
                print("No edges, something is wrong")
                self.valid = False
                print("no edges left")
                return []
            edge = random.choice(edges)
            edges.remove(edge)
            # Try to start on this edge, and exit the loop if it works
            second_points = self._try_start_edge(edge, directions)
            if second_points:
                found_point = True

        # If it didn't work at all, return now before sorting out the extra points
        if not second_points:
            return []

        # Need to find which direction has the body of the octopus
        # Then create two points towards it to create a clean seam
        for direction in directions:
            body_point = [
                second_points[0][0] + direction[0],
                second_points[0][1] + direction[1],
                second_points[0][2] + direction[2],
            ]
            # It is on the body, so we've found the right direction and can create the points
            if self.shape.grid[body_point[0]][body_point[1]][body_point[2]]:
                first_points = [body_point]
                # Remove the body from the grid because we don't want to check for intersection with it
                old_grid = copy.copy(self.grid)
                self.grid = self.grid != self.shape.grid
                # Add the border around the body
                if not self._add_point_and_border(
                    first_points, direction, self.min_width
                ):
                    # Didn't work, so return empty and fix up the grid
                    self.grid = old_grid
                    continue  # try a different direction
                # Do it one more time for a nice seam
                zero_point = [
                    body_point[0] + direction[0],
                    body_point[1] + direction[1],
                    body_point[2] + direction[2],
                ]
                zero_points = [zero_point]
                if not self._add_point_and_border(
                    zero_points, direction, self.min_width
                ):
                    self.grid = old_grid
                    continue  # try a different direction

                # Finished with the points, add back in the right body.
                self.grid = old_grid

                # Add in the initial point and the two seams
                all_points.append(zero_points)
                all_points.append(first_points)
                all_points.append(second_points)

                # Add in enough forward directions for the width.
                forward_direction = [-x for x in direction]
                for _ in range(self.min_width):
                    if not self._try_add(forward_direction, all_points):
                        continue  # try a different direction
                return all_points

        # At this point, either we found a good point off the edge
        # so we're returning that point and will make a tentacle with it
        # or we did not and we're returning an empty list and will try again
        if not all_points:
            print("at the end")
        return all_points

    def _try_start_edge(self, edge, directions):
        old_grid = copy.copy(self.grid)
        self.grid = self.grid != self.shape.grid
        for direction in directions:
            try:  # skip if this is out of bounds
                test_point = [
                    edge[0] + direction[0],
                    edge[1] + direction[1],
                    edge[2] + direction[2],
                ]
                if not (self.grid[test_point[0]][test_point[1]][test_point[2]]):
                    if not intersect_or_touch(test_point, self.full_grid):
                        second_points = [test_point]
                        if not self._add_point_and_border(
                            second_points, direction, self.min_width
                        ):
                            self.grid = old_grid
                            return []
                        self.grid = old_grid
                        return second_points
            except:
                pass
        self.grid = old_grid
        return []

    # Stop if the path is long enough
    def _stop_walk_condition(self, all_points):
        if len(all_points) >= self.tentacle_length:
            return True
        return False

    # Valid if it's as long or longer than the minimal acceptable length
    def _acceptable_walk(self, all_points):
        if len(all_points) >= self.min_tentacle_length:
            return True
        return False
