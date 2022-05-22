import math
import numpy as np
import random
import yaml
import itertools
from operator import add

from Geometry import intersect_or_touch, rotate_grid, distance3d, forward
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

        self._place()

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
    def random(cls, grid, shape_config, random_walk_config):
        # Read values from config file
        with open(shape_config, "r") as stream:
            data_loaded = yaml.safe_load(stream)
        center_place = data_loaded["Torus"]["center_placement_border"]
        min_major = data_loaded["Torus"]["min_major_radius"]
        max_major = data_loaded["Torus"]["max_major_radius"]
        min_minor = data_loaded["Torus"]["min_minor_radius"]
        size = grid[0][0].size

        # Make random torus
        rotation = [
            random.choice([0, math.pi]),
            random.choice([0, math.pi]),
            random.choice([0, math.pi]),
        ]
        center = [
            random.randrange(center_place, size - center_place, 1),
            random.randrange(center_place, size - center_place, 1),
            random.randrange(center_place, size - center_place, 1),
        ]
        if min_major == max_major:
            major_radius = min_major
        else:
            major_radius = random.randrange(min_major, max_major, 1)

        if min_minor == (major_radius - 2):
            minor_radius = min_minor
        else:
            minor_radius = random.randrange(min_minor, major_radius - 2, 1)
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
        self._place()

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
    def random(cls, grid, shape_config, random_walk_config, torus_holes=0):
        # Read values from config file
        with open(shape_config, "r") as stream:
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
            random.choice([0, math.pi]),
            random.choice([0, math.pi]),
            random.choice([0, math.pi]),
        ]
        center = [
            random.randrange(center_place, size - center_place, 1),
            random.randrange(center_place, size - center_place, 1),
            random.randrange(center_place, size - center_place, 1),
        ]
        if min_major == max_major:
            major_radius = min_major
        else:
            major_radius = random.randrange(min_major, max_major, 1)

        if min_minor == (major_radius - 2):
            minor_radius = min_minor
        else:
            minor_radius = random.randrange(min_minor, major_radius - 2, 1)

        # If they're the same, just use that number
        # otherwise do it randomly
        if torus_holes != 0:
            n_holes = torus_holes
        else:
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


# A torus with any number of holes. Rather than using shape equations, it forms itself by using random walks
class TorusFree(object):
    # Make a specific torus
    def __init__(
        self, full_grid, center, n_holes, donut_length
    ):
        # Set torus information
        self.full_grid = full_grid
        self.center = center
        self.n_holes = n_holes
        self.valid = False
        self.grid = full_grid & ~full_grid  # initialise to empty
        self.length = donut_length

        while intersect_or_touch(self.center, full_grid):
            self.center = [
                random.randrange(0, full_grid[0][0].size - 1, 1),
                random.randrange(0, full_grid[0][0].size - 1, 1),
                random.randrange(0, full_grid[0][0].size - 1, 1),
            ]

        # Keep trying to make the donut until it's made
        while not self.valid:
            self.grid = full_grid & ~full_grid  # initialise to empty
            self.valid = self._create_grid()


        
        # do draw grid stuff
        self.draw_grid = self.grid

    # Make a random torus
    @classmethod
    def random(cls, grid, shape_config, random_walk_config, torus_holes=0):
        # Read values from config file
        with open(shape_config, "r") as stream:
            data_loaded = yaml.safe_load(stream)
        center_place = data_loaded["Torus"]["center_placement_border"]
        max_holes = data_loaded["Torus"]["max_holes"]
        min_holes = data_loaded["Torus"]["min_holes"]
        donut_length = data_loaded["Torus"]["length"]
        size = grid[0][0].size

        # Make random torus
        center = [
            random.randrange(center_place, size - center_place, 1),
            random.randrange(center_place, size - center_place, 1),
            random.randrange(center_place, size - center_place, 1),
        ]
        
        # If they're the same, just use that number
        # otherwise do it randomly
        if torus_holes != 0:
            n_holes = torus_holes
        else:
            if max_holes == min_holes:
                n_holes = min_holes
            else:
                n_holes = random.randrange(min_holes, max_holes + 1, 1)

        return cls(grid, center, n_holes, donut_length)

    # When creating the grid, plug up the torus so place and move
    # can detect if there's anything going through the torus
    def _create_grid(self):

        all_points = self._walk(self.center)
        print("a", all_points)
        if not all_points:
            return False
        for point in all_points:
            self.grid[point[0]][point[1]][point[2]] = True

        for _ in range(0, self.n_holes-1):
            points = self._walk(random.choose(all_points))
            if not points:
                return False
            for point in points:
                all_points.append(point)
                self.grid[point[0]][point[1]][point[2]] = True
        return True


    def _walk(self, center):
        # Add all possible movement directions
        movement_direction = []  # list of value movements
        for x, y, z in itertools.permutations([1, 0, 0], 3):
            movement_direction.append([x, y, z])
            movement_direction.append([-x, -y, -z])
        movement_direction.sort()
        # Remove duplicates
        movement_direction = list(
            movement_direction
            for movement_direction, _ in itertools.groupby(movement_direction)
        )

        all_points = [center]
        print("walking", all_points)
        while not self._stop_walk_condition(all_points):
            point_added = False
            random.shuffle(movement_direction)
            
            if len(all_points) > self.length / 2:
                movement_direction = self.directions(all_points[0], all_points[-1])
                print(movement_direction)
            
            for direction in movement_direction:
                # Add the direction and the last point
                new_point = list(map(add, direction, all_points[-1]))
                if self._allowed_point(new_point, all_points):
                    all_points.append(new_point)
                    # Add onto the grid the point from two runs ago
                    if len(all_points) > 2:
                        to_add = all_points[len(all_points) - 3]
                        self.grid[to_add[0], to_add[1], to_add[2]] = True
                    point_added = True
                    break  # Don't keep going with the for loop
                else:
                    print("failed")
                    print(all_points)
                    print(new_point)
            # If a point wasn't added
            # see if this was a decent enough try
            # otherwise just return false
            if not point_added:
                print(all_points)
                return []
        return all_points

    def directions(self, center, end):
        directions = []
        if center[0] != end[0]:
            if center[0] < end[0]:
                directions.append([-1,0,0])
            else:
                directions.append([1,0,0])
        
        if center[1] != end[1]:
            if center[1] < end[1]:
                directions.append([0,-1,0])
            else:
                directions.append([0,1,0])
        
        if center[2] != end[2]:
            if center[2] < end[2]:
                directions.append([0,0,-1])
            else:
                directions.append([0,0,1])
        
        return directions
        

    def _allowed_point(self, new_point, all_points):
        # Don't repeat ourselves
        if all_points.count(new_point) > 0:
            if new_point == all_points[0]:
                if len(all_points) < self.length / 2:
                    print("Tried revisiting before length big")
                    return False
                return True
            print("tried revisiting and it's not the first point")
            return False

        if intersect_or_touch(new_point, self.full_grid):
            print("touched the full grid")
            return False

        # this is the yikes one where it could graze past 
        # and we need to make it go there, not just touch and go away
        if intersect_or_touch(new_point, self.grid):
            # if the length is too short, don't let it go here
            if len(all_points) < self.length / 2:
                print("touched the torus but it's too early")
                return False
            # otherwise check it is actually going toward the start
            difference = forward(new_point, all_points[0])
            print(difference)
            for i in difference:
                if i > 1 or i < -1:
                    print("touched something but it's too far away to be the first point")
                    return False

        return True

    def _stop_walk_condition(self, all_points):
        if len(all_points) < self.length / 2:
            return False
        if all_points[-1] == all_points[0]:
            return True
        return False

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

    # Torus is only one voxel thick, any point is valid 
    def _valid_edge(self, point):
        return True

    