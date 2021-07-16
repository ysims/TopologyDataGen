import itertools
import random
import yaml

from Geometry import intersect_or_touch, hard_surrounded
from RandomWalk import RandomWalk
from Spheroid import Spheroid


class Octopus(RandomWalk):

    def __init__(self, 
                full_grid, 
                num_tentacles, 
                min_tentacle_length, 
                max_tentacle_length):
        self.sphere = Spheroid.random(full_grid)
        while not self.sphere.valid:
            self.sphere = Spheroid.random(full_grid)
        self.grid = self.sphere.grid
        self.full_grid = full_grid
        self.num_tentacles = num_tentacles
        self.min_tentacle_length = min_tentacle_length
        self.max_tentacle_length = max_tentacle_length
        self.valid = True

        # Add the number of tentacles that we want
        # Retry if it fails
        for _ in range(num_tentacles):
            while not self._random_walk():
                continue

    # Make a random tunnel
    @classmethod
    def random(cls, full_grid):
        # Read values from config file
        with open("./Objects/config/RandomWalk.yaml", 'r') as stream:
            data_loaded = yaml.safe_load(stream)
        min_num_tentacles = data_loaded["Octopus"]["min_num_tentacles"]
        max_num_tentacles = data_loaded["Octopus"]["max_num_tentacles"]
        min_tentacle_length = data_loaded["Octopus"]["min_tentacle_length"]
        max_tentacle_length = data_loaded["Octopus"]["max_tentacle_length"]

        num_tentacles = random.randrange(min_num_tentacles,
            max_num_tentacles, 1)
        return cls(full_grid, num_tentacles, 
            min_tentacle_length, max_tentacle_length)

    def _allowed_point(self, new_point):
        if intersect_or_touch(new_point, (self.grid | self.full_grid)):
            return False
        return True

    # Determines a start location for the walk
    # and returns the first point in the walk
    def _get_start(self):
        # Determine length of the tentacle
        self.tentacle_length = random.randrange(self.min_tentacle_length, 
            self.max_tentacle_length, 1)
        all_points = []
        
        # We will make a 'tentacle' going off from one of the edges
        edges = []
        for X,Y,Z in itertools.product(range(0, self.full_grid[0][0].size), repeat=3):
            if (self.sphere.grid[X][Y][Z] 
                    and not hard_surrounded([X,Y,Z], self.grid)):
                edges.append([X,Y,Z])
        
        if not edges:
            print("No edges, something is wrong")
            self.valid = False
            return []

        # Grab a random edge to use
        # Don't add it to the path because it's already on the circle
        # Find one open spot to add to the path
        edge = random.choice(edges)
        directions = [[1,0,0],[0,1,0],[0,0,1],[-1,0,0],[0,-1,0],[0,0,-1]]
        for direction in directions:
            try:    # skip if this is out of bounds
                test_point = [edge[0] + direction[0],
                              edge[1] + direction[1],
                              edge[2] + direction[2]]
                if not (self.grid[test_point[0]]
                                 [test_point[1]]
                                 [test_point[2]]):  
                    if not intersect_or_touch(test_point, self.full_grid):
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