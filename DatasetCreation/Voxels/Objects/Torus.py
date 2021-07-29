import math
import numpy as np
import random
import yaml

from Geometry import intersect_or_touch, rotate_grid, distance3d
from Shape import Shape


class Torus(Shape):
    # Make a specific torus
    def __init__(self, full_grid, center, major_radius, minor_radius, rotation):
        # Check we can even go here in the first place
        if intersect_or_touch(center, full_grid):
            self.valid = False
            return

        # Set torus information
        self.full_grid = full_grid
        self.center = center
        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.rotation = rotation
        self.valid = True

        size = full_grid[0][0].size
        self.x, self.y, self.z = rotate_grid(size, self.rotation, self.center)

        self._place_and_move()

        # place_and_move uses a grid that is plugged up for intersection checking
        # In the end, we don't want this so just make the torus normally
        self.draw_grid = (
            pow(
                np.sqrt((self.x - self.center[0]) ** 2 + (self.y - self.center[1]) ** 2)
                - self.major_radius,
                2,
            )
            + (self.z - self.center[2]) ** 2
            <= self.minor_radius ** 2
        )

    # Make a random torus
    @classmethod
    def random(cls, grid):
        # Read values from config file
        with open("./Objects/config/Shape.yaml", "r") as stream:
            data_loaded = yaml.safe_load(stream)
        center_place = data_loaded["Torus"]["center_placement_border"]
        min_major = data_loaded["Torus"]["min_major_radius"]
        max_major = data_loaded["Torus"]["max_major_radius"]
        min_minor = data_loaded["Torus"]["min_minor_radius"]
        size = grid[0][0].size

        # Make random torus
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
        major_radius = random.randrange(min_major, max_major, 1)
        minor_radius = random.randrange(min_minor, major_radius - 1, 1)
        return cls(grid, center, major_radius, minor_radius, rotation)

    # This will get the circle that 'plugs' up the torus
    # to prevent tunnels going through
    def get_disc(self):
        disc = (
            (self.z > self.center[2] - 1)
            & (self.z < self.center[2] + 1)
            & (
                (self.x - self.center[0]) ** 2 + (self.y - self.center[1]) ** 2
                <= self.major_radius ** 2
            )
        )
        return disc

    # Function required for place_and_move function
    def _create_grid(self):
        # Make a voxelised torus and rotate it
        self.grid = (
            pow(
                np.sqrt((self.x - self.center[0]) ** 2 + (self.y - self.center[1]) ** 2)
                - self.major_radius,
                2,
            )
            + (self.z - self.center[2]) ** 2
            <= self.minor_radius ** 2
        )

        # Since this grid is used to check intersections,
        # add in the disc so we don't get things
        # going through the torus
        self.grid = self.grid | self.get_disc()

    # Checks if a point is a valid edge point
    # For a torus, we don't want the inner edges counting
    def _valid_edge(self, point):
        if distance3d(point, self.center) <= self.major_radius:
            return False
        return True


# A 2-torus
class TorusN(Shape):
    # Make a specific torus
    def __init__(
        self, full_grid, center, major_radius, minor_radius, rotation, n_holes
    ):
        # Set torus information
        self.full_grid = full_grid
        self.center = center
        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.rotation = rotation
        self.n_holes = n_holes
        self.valid = True
        size = full_grid[0][0].size
        self.x, self.y, self.z = rotate_grid(size, self.rotation, self.center)

        # Find a center that works
        self._place_and_move()

        # Make the grid properly now that we've got a valid center
        self.draw_grid = (self.x == 0) & (self.x == 1)
        for i in range(self.n_holes):
            torus = (
                pow(
                    np.sqrt(
                        (self.x - self.center[0] + i * self.major_radius * 2) ** 2
                        + (self.y - self.center[1]) ** 2
                    )
                    - self.major_radius,
                    2,
                )
                + (self.z - self.center[2]) ** 2
                <= self.minor_radius ** 2
            )
            self.draw_grid = self.draw_grid | torus

    # Make a random torus
    @classmethod
    def random(cls, grid):
        # Read values from config file
        with open("./Objects/config/Shape.yaml", "r") as stream:
            data_loaded = yaml.safe_load(stream)
        center_place = data_loaded["Torus"]["center_placement_border"]
        min_major = data_loaded["Torus"]["min_major_radius"]
        max_major = data_loaded["Torus"]["max_major_radius"]
        min_minor = data_loaded["Torus"]["min_minor_radius"]
        max_holes = data_loaded["Torus"]["max_holes"]
        min_holes = data_loaded["Torus"]["min_holes"]
        size = grid[0][0].size

        # Make random torus
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
        major_radius = random.randrange(min_major, max_major + 1, 1)
        minor_radius = random.randrange(min_minor, major_radius, 1)

        # If they're the same, just use that number
        # otherwise do it randomly
        if max_holes == min_holes:
            n_holes = min_holes
        else:
            n_holes = random.randrange(min_holes, max_holes + 1, 1)

        return cls(grid, center, major_radius, minor_radius, rotation, n_holes)

    # When creating the grid, plug up the torus so place and move
    # can detect if there's anything going through the torus
    def _create_grid(self):
        self.grid = (self.x == 0) & (self.x == 1)
        for i in range(self.n_holes):
            torus = (
                pow(
                    np.sqrt(
                        (self.x - self.center[0] + i * self.major_radius * 2) ** 2
                        + (self.y - self.center[1]) ** 2
                    )
                    - self.major_radius,
                    2,
                )
                + (self.z - self.center[2]) ** 2
                <= self.minor_radius ** 2
            )
            self.grid = self.grid | torus
        self.grid = self.grid | self.get_disc()

    # This will get the circle that 'plugs' up the torus,
    # to prevent tunnels going through
    def get_disc(self):
        combined_disc = (self.x == 0) & (self.x == 1)
        for i in range(self.n_holes):
            disc = (
                (self.z > self.center[2] - 1)
                & (self.z < self.center[2] + 1)
                & (
                    (self.x - self.center[0] + i * self.major_radius * 2) ** 2
                    + (self.y - self.center[1]) ** 2
                    <= self.major_radius ** 2
                )
            )
            combined_disc = combined_disc | disc
        return combined_disc

    # Only valid if it's not in the inner part of either torus
    def _valid_edge(self, point):
        # Can't be inside the first torus
        if distance3d(point, self.center) <= self.major_radius:
            return False
        # Can't be inside the second torus
        second_center = [(x + self.major_radius * 2) for x in self.center]
        if distance3d(point, second_center) <= self.major_radius:
            return False
        return True
