import copy
import itertools
import math
from operator import add
import random
import yaml
import numpy as np

from Geometry import intersect_or_touch, hard_surrounded, forward
from RandomWalk import RandomWalk
from Spheroid import Spheroid
from Torus import Torus, TorusN


class Octopus(RandomWalk):
    def __init__(self, full_grid, num_tentacles, random_walk_config, shape_config, shape):
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
        
        if shape == "":
            self.shape_name = data_loaded["Octopus"]["shape"]
        else:
            self.shape_name = shape

        if self.shape_name == "Spheroid":
            self.shape = Spheroid.random(full_grid, shape_config, random_walk_config)
            while not self.shape.valid:
                self.shape = Spheroid.random(
                    full_grid, shape_config, random_walk_config
                )
        elif self.shape_name == "Torus2":
            self.shape = TorusN.random(full_grid, shape_config, random_walk_config, 2)
            while not self.shape.valid:
                self.shape = TorusN.random(
                    full_grid, shape_config, random_walk_config, 2
                )
        elif self.shape_name == "Torus3":
            self.shape = TorusN.random(full_grid, shape_config, random_walk_config, 3)
            while not self.shape.valid:
                self.shape = TorusN.random(
                    full_grid, shape_config, random_walk_config, 3
                )
        elif self.shape_name == "Torus":
            self.shape = Torus.random(full_grid, shape_config, random_walk_config)
            while not self.shape.valid:
                self.shape = Torus.random(full_grid, shape_config, random_walk_config)
        else:
            print("Error: Not a valid shape for the octopus.")
            return


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
        return cls(full_grid, num_tentacles, random_walk_config, shape_config, "")

    @classmethod
    def random(cls, full_grid, shape_config, random_walk_config, shape):
        # Read values from config file
        with open(random_walk_config, "r") as stream:
            data_loaded = yaml.safe_load(stream)
        min_num_tentacles = data_loaded["Octopus"]["min_num_tentacles"]
        max_num_tentacles = data_loaded["Octopus"]["max_num_tentacles"]

        num_tentacles = random.randrange(min_num_tentacles, max_num_tentacles, 1)
        return cls(full_grid, num_tentacles, random_walk_config, shape_config, shape)


    def _allowed_point(self, new_point, all_points):
        # Don't repeat ourselves
        if all_points.count(new_point) > 0:
            return False

        # If we're still close to the body,
        # don't worry about touching the body
        if len(all_points) < 2:
            if intersect_or_touch(new_point, self.full_grid):
                return False
        else:
            if intersect_or_touch(new_point, (self.grid | self.full_grid)):
                return False
        return True

    # Separate function for adding the tentacles
    # Since it'd be better to add them all later
    # Since they're easier to add than big objects
    def addTentacles(self, full_grid):
        self.full_grid = full_grid & (~self.grid)

        max_tries = 100
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
                return []
            edge = random.choice(edges)
            edges.remove(edge)

            for direction in directions:
                try:  # skip if this is out of bounds
                    test_point = [
                        edge[0] + direction[0],
                        edge[1] + direction[1],
                        edge[2] + direction[2],
                    ]
                    if not (self.grid[test_point[0]][test_point[1]][test_point[2]]):
                        if not intersect_or_touch(test_point, self.full_grid):
                            found_point = True
                            all_points.append(test_point)
                            break
                except:
                    pass

        # At this point, either we found a good point off the edge
        # so we're returning that point and will make a tentacle with it
        # or we did not and we're returning an empty list and will try again
        return all_points

    # Stop if the path is long enough
    def _stop_walk_condition(self, all_points):
        if len(all_points) is self.tentacle_length:
            return True
        return False

    # Valid if it's as long or longer than the minimal acceptable length
    def _acceptable_walk(self, all_points):
        if len(all_points) >= self.min_tentacle_length:
            return True
        return False

    # Given the path, how many times will we branch from it?
    def _num_branches(self, path):
        # -2 from endpoints (no branches on endpoints)
        if len(path) < self.length_between_branches - 2:
            return 0
        return math.floor(len(path) / self.length_between_branches)

    # Find a point to branch from on the path
    # and return the beginning of the new path
    def _branch_start(self, _path):
        # This tentacle will be smaller than its parent
        if int(len(_path) / 2) <= int(self.min_tentacle_length / 2):
            return []
        self.tentacle_length = random.randrange(
            int(self.min_tentacle_length / 2), int(len(_path) / 2), 1
        )

        path = copy.copy(_path)

        # This is the path we choose a point from
        # It has the first and last taken out
        choice_path = copy.copy(_path)
        choice_path.pop(0)
        choice_path.pop(len(choice_path) - 1)

        new_path = []
        max_tries = 1000
        amount_tried = 0
        while (not new_path) and (amount_tried < max_tries):
            amount_tried += 1

            path = copy.copy(_path)
            start = random.choice(choice_path)

            # Remove this point and adjacent points so we can
            # do intersect or touch properly
            index = path.index(start)
            before = path.pop(index - 1)
            # The index has changed because we just popped
            # Go back one for all
            after = path.pop(index)

            # direction1 = forward(before, start)
            # direction2 = forward(start, after)
            # if direction1 != direction2:
            #     continue
            
            self.grid[start[0]][start[1]][start[2]] = False
            self.grid[before[0]][before[1]][before[2]] = False
            self.grid[after[0]][after[1]][after[2]] = False


            directions = [
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
                [-1, 0, 0],
                [0, -1, 0],
                [0, 0, -1],
            ]
            for direction in directions:
                try:  # skip if this is out of bounds
                    start_path = list(map(add, direction, start))
                    if start_path is before:
                        continue
                    if start_path is after:
                        continue
                    # start_path point is valid and by adding it to the list
                    # we are breaking out of the while loop
                    if not intersect_or_touch(start_path, (self.grid | self.full_grid)):
                        new_path.append(start_path)
                        break
                except:
                    pass

            self.grid[start[0]][start[1]][start[2]] = True
            self.grid[before[0]][before[1]][before[2]] = True
            self.grid[after[0]][after[1]][after[2]] = True

        return new_path
