import copy
import itertools
import math
from operator import add
import random
import yaml

from Geometry import intersect_or_touch, hard_surrounded
from RandomWalk import RandomWalk
from Spheroid import Spheroid
from Torus import Torus


class Octopus(RandomWalk):
    def __init__(self, full_grid, num_tentacles):
        self.full_grid = full_grid
        self.num_tentacles = num_tentacles
        self.valid = True
        self.width = 2
        # Read values from config file
        with open("./Objects/config/RandomWalk.yaml", "r") as stream:
            data_loaded = yaml.safe_load(stream)
        self.min_tentacle_length = data_loaded["Octopus"]["min_tentacle_length"]
        self.max_tentacle_length = data_loaded["Octopus"]["max_tentacle_length"]
        self.branching = data_loaded["Octopus"]["branching"]
        self.length_between_branches = data_loaded["Octopus"]["length_between_branches"]
        self.shape_name = data_loaded["Octopus"]["shape"]

        if self.shape_name == "Spheroid":
            self.shape = Spheroid.random(full_grid)
            while not self.shape.valid:
                self.shape = Spheroid.random(full_grid)
        else:
            self.shape = Torus.random(full_grid)
            while not self.shape.valid:
                self.shape = Torus.random(full_grid)

        self.grid = copy.copy(self.shape.draw_grid)

    # Make a random tunnel
    @classmethod
    def random(cls, full_grid):
        # Read values from config file
        with open("./Objects/config/RandomWalk.yaml", "r") as stream:
            data_loaded = yaml.safe_load(stream)
        min_num_tentacles = data_loaded["Octopus"]["min_num_tentacles"]
        max_num_tentacles = data_loaded["Octopus"]["max_num_tentacles"]

        num_tentacles = random.randrange(min_num_tentacles, max_num_tentacles, 1)
        return cls(full_grid, num_tentacles)

    def _try_add(self, direction, all_points):
        next_point = list(map(add, direction, all_points[len(all_points) - 1][0]))
        if intersect_or_touch(next_point, (self.grid | self.full_grid)):
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
                if not intersect_or_touch(test_point, (self.grid | self.full_grid)):
                    points_to_be_added.append(test_point)
                else:
                    return False
            except:
                pass

        all_points.append(points_to_be_added)

        if len(all_points) > 4:
            last_index = len(all_points) - 2 - self.width
            for i in range(0, last_index + 1):
                for point in all_points[i]:
                    self.grid[point[0]][point[1]][point[2]] = True

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

    # Determines a start location for the walk
    # and returns the first point in the walk
    def _get_start(self):
        # Determine length of the tentacle
        self.tentacle_length = random.randrange(
            self.min_tentacle_length, self.max_tentacle_length, 1
        )
        all_points = []
        second_points = []
        # We will make a 'tentacle' going off from one of the edges
        edges = []
        for X, Y, Z in itertools.product(range(0, self.full_grid[0][0].size), repeat=3):
            if self.shape.draw_grid[X][Y][Z] and not hard_surrounded(
                [X, Y, Z], self.grid
            ):
                edges.append([X, Y, Z])

        if not edges:
            print("No edges, something is wrong")
            self.valid = False
            return []

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
                            second_points.append(test_point)
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
                                    second_surrounds = [
                                        test_point[0] + border[0],
                                        test_point[1] + border[1],
                                        test_point[2] + border[2],
                                    ]
                                    # Don't care about intersection in this case
                                    # it will definitely intersect with the body
                                    # and that is ok
                                    second_points.append(second_surrounds)
                                except:
                                    pass
                            break
                except:
                    pass

        # If it didn't work, return now before sorting out the extra points
        if not second_points:
            return []

        # Need to find which direction has the body of the octopus
        for direction in directions:
            body_point = [
                second_points[0][0] + direction[0],
                second_points[0][1] + direction[1],
                second_points[0][2] + direction[2],
            ]
            if self.grid[body_point[0]][body_point[1]][body_point[2]]:
                # We've found the body
                first_points = [body_point]
                # Add the border around the body
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
                        body_surrounds = [
                            body_point[0] + border[0],
                            body_point[1] + border[1],
                            body_point[2] + border[2],
                        ]
                        # Don't care about intersection in this case
                        # it will definitely intersect with the body
                        # and that is ok
                        first_points.append(body_surrounds)
                    except:
                        pass

                zero_point = [
                    body_point[0] + direction[0],
                    body_point[1] + direction[1],
                    body_point[2] + direction[2],
                ]
                zero_points = [zero_point]
                for border in add_border:
                    try:  # skip if this is out of bounds
                        zero_surrounds = [
                            zero_point[0] + border[0],
                            zero_point[1] + border[1],
                            zero_point[2] + border[2],
                        ]
                        # Don't care about intersection in this case
                        # it will definitely intersect with the body
                        # and that is ok
                        zero_points.append(zero_surrounds)
                    except:
                        pass

                all_points.append(zero_points)
                all_points.append(first_points)
                all_points.append(second_points)
                forward_direction = [-x for x in direction]
                for _ in range(self.width):
                    if not self._get_next_point(
                        all_points, forward_direction, add_border
                    ):
                        return []
                return all_points

        # At this point, either we found a good point off the edge
        # so we're returning that point and will make a tentacle with it
        # or we did not and we're returning an empty list and will try again
        return all_points

    # Try to add another point after the starting point/s
    def _get_next_point(self, all_points, forward_direction, add_border):
        next_point = list(
            map(add, forward_direction, all_points[len(all_points) - 1][0])
        )
        # Check if the point is valid
        if intersect_or_touch(next_point, self.full_grid):
            return []
        points_to_be_added = [next_point]
        for border in add_border:
            try:  # skip if this is out of bounds
                test_point = [
                    next_point[0] + border[0],
                    next_point[1] + border[1],
                    next_point[2] + border[2],
                ]
                if not intersect_or_touch(test_point, self.full_grid):
                    points_to_be_added.append(test_point)
                else:
                    return False
            except:
                pass
        all_points.append(points_to_be_added)
        return True

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

            # Get the direction
            start_point = start[0]
            before_point = before[0]
            direction = [
                start_point[0] - before_point[0],
                start_point[1] - before_point[1],
                start_point[2] - before_point[2],
            ]
            directions = (
                [[0, 1, 0], [0, 0, 1], [0, -1, 0], [0, 0, -1]]
                if direction[0] == 0
                else [
                    [1, 0, 0],
                    [0, 0, 1],
                    [-1, 0, 0],
                    [0, 0, -1],
                ]
                if direction[0] == 0
                else [
                    [1, 0, 0],
                    [0, 1, 0],
                    [-1, 0, 0],
                    [0, -1, 0],
                ]
            )
            random.shuffle(directions)

            for i in range(index - 2, index + 2):
                for point in _path[i]:
                    self.grid[point[0]][point[1]][point[2]] = False

            for direction in directions:
                new_start = [
                    start_point[0] + direction[0],
                    start_point[1] + direction[1],
                    start_point[2] + direction[2],
                ]
                new_points = [new_start]

                if intersect_or_touch(new_start, (self.grid | self.full_grid)):
                    continue
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
                        new_surrounds = [
                            new_start[0] + border[0],
                            new_start[1] + border[1],
                            new_start[2] + border[2],
                        ]
                        if not intersect_or_touch(
                            new_start, (self.grid | self.full_grid)
                        ):
                            new_points.append(new_surrounds)
                        else:
                            continue
                    except:
                        pass
                new_path = [new_points]

            for i in range(index - 2, index + 2):
                for point in _path[i]:
                    self.grid[point[0]][point[1]][point[2]] = True

        return new_path
