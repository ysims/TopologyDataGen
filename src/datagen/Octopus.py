import copy
import itertools
import math
from operator import add
import random
import yaml
import numpy as np
import scipy.ndimage

from RandomWalk import RandomWalk
from Spheroid import Spheroid
from Torus import Torus, TorusN
import utils


class Octopus(RandomWalk):
    def __init__(self, full_grid, num_tentacles, random_walk_config, shape_config):
        self.full_grid = full_grid
        self.num_tentacles = num_tentacles
        self.valid = True
        self.isBranching = False

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
        self.object_min_distance = data_loaded["object_min_distance"]
        self.min_branch_length = int(self.min_tentacle_length / 2)

        if self.shape_name == "Spheroid":
            self.shape = Spheroid.random(full_grid, shape_config, random_walk_config)
            while not self.shape.valid:
                self.shape = Spheroid.random(
                    full_grid, shape_config, random_walk_config
                )
            print("Sphere")
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
            self.draw_grid = self.grid
            # Create the occupancy grid with the shape plus a thickness to stop the paths from approaching the shape too closely
            # Create an external version of everything else in the cube
            # Add this external version to the occupancy grid
            self.occupancy_grid = scipy.ndimage.binary_dilation(
                self.grid,
                scipy.ndimage.generate_binary_structure(3, 3),
                iterations=(self.object_min_distance),
            )
            self.external_occupancy_grid = scipy.ndimage.binary_dilation(
                self.full_grid,
                scipy.ndimage.generate_binary_structure(3, 3),
                iterations=(self.object_min_distance),
            )

            self.occupancy_grid = self.occupancy_grid | self.external_occupancy_grid
            self.tentacle_occupancy = self.occupancy_grid != self.occupancy_grid

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

        self.external_occupancy_grid = scipy.ndimage.binary_dilation(
            self.full_grid,
            scipy.ndimage.generate_binary_structure(3, 3),
            iterations=(self.object_min_distance),
        )

        self.occupancy_grid = self.occupancy_grid | self.external_occupancy_grid


        # Add the number of tentacles that we want
        # Retry if it fails
        max_tries = 1000
        tries = 0
        for i in range(self.num_tentacles):
            tries = 0
            while not self._random_walk():
                tries += 1
                if tries >= max_tries:
                    self.valid = False
                    break
                continue

        self.draw_grid = self.grid

    # Returns True if the point is closer than object_min_distance
    # to existing objects in the grid or the border,
    # or is closer than one voxel to itself.
    # Returns False otherwise
    def _grid_check(self, point):
        if self.occupancy_grid[point[0]][point[1]][point[2]]:
            return True
        return False

    def _get_start(self):
        # Determine length of the tentacle
        self.tentacle_length = random.randrange(
            self.min_tentacle_length, self.max_tentacle_length, 1
        )

        # Get the shell of the body and add the points to the list of edges
        shape_shell = utils.shell(self.shape.grid).numpy()
        edges = []
        for X, Y, Z in itertools.product(range(0, shape_shell[0][0].size), repeat=3):
            if shape_shell[X][Y][Z]:
                edges.append([X, Y, Z])

        if not edges:
            print("No edges in initial find. Something is wrong.")
            return []

        # Loop until a start is found or there are no more edges
        directions = []
        for x, y, z in itertools.permutations([1, 0, 0], 3):
            if directions.count([x, y, z]) == 0:
                directions.append([x, y, z])
            if directions.count([-x, -y, -z]) == 0:
                directions.append([-x, -y, -z])
        while edges:
            # Take a random edge and check if any tentacles are too close
            edge = random.choice(edges)
            edges.remove(edge)
            if utils.exists_grid(self.tentacle_occupancy, edge):
                continue  # loop back around and try a different edge

            # Create the path list with enough points to escape the occupancy grid from the body
            path = [[edge]]
            # Find the right direction to go in
            random.shuffle(directions)
            for direction in directions:
                borders = utils.border(direction, self.min_width)
                if utils.exists_grid(
                    self.shape.grid, utils.add_points(edge, direction)
                ):
                    continue  # this is the body direction, try again
                failed = False
                for _ in range(self.object_min_distance):
                    if utils.exists_grid(
                        (self.tentacle_occupancy | self.external_occupancy_grid),
                        utils.add_points(path[len(path) - 1][0], direction),
                    ):
                        # Didn't work, collided with another object or tentacle
                        # Break the for and try another direction
                        failed = True
                        break
                    # Add the point to the path
                    path.append([utils.add_points(path[len(path) - 1][0], direction)])
                if not failed:
                    # Add a point right at the beginning of the path going backwards, for a clean seam
                    path.insert(0, [utils.add_points(path[0][0], [-x for x in direction])])
                    for points in path:
                        for border in borders:
                            points.append(utils.add_points(points[0], border))
                    break
            if not failed:
                return path
            # If it did fail, loop back around and try a different edge
        # If it reaches this point, it didn't find anywhere appropriate
        print("No edges were successful in starting a tentacle. Something is wrong.")
        return []

    # Stop if the path is long enough
    def _stop_walk_condition(self, path):
        if self.isBranching:
            if len(path) >= self.branch_length:
                return True
            return False
        if len(path) >= self.tentacle_length:
            return True
        return False

    # Valid if it's as long or longer than the minimal acceptable length
    def _acceptable_walk(self, path):
        if self.isBranching:
            if len(path) >= self.min_branch_length:
                return True
            return False
        if len(path) >= self.min_tentacle_length:
            return True
        return False
