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
        
        # Read values from config file
        with open("./Objects/config/RandomWalk.yaml", 'r') as stream:
            data_loaded = yaml.safe_load(stream)
        self.min_tentacle_length = data_loaded["Octopus"]["min_tentacle_length"]
        self.max_tentacle_length = data_loaded["Octopus"]["max_tentacle_length"]
        self.branching = data_loaded["Octopus"]["branching"]
        self.length_between_branches = \
            data_loaded["Octopus"]["length_between_branches"]
        self.shape_name = data_loaded["Octopus"]["shape"]

        if self.shape_name is "Spheroid":
            self.shape = Spheroid.random(full_grid)
            while not self.shape.valid:
                self.shape = Spheroid.random(full_grid)
            self.grid = copy.copy(self.shape.draw_grid)
        else:
            self.shape = Torus.random(full_grid)
            while not self.shape.valid:
                self.shape = Torus.random(full_grid)
            self.grid = copy.copy(self.shape.draw_grid)


        # Add the number of tentacles that we want
        # Retry if it fails
        for _ in range(num_tentacles):
            while not self._random_walk():
                continue

        self.draw_grid = self.grid

    # Make a random tunnel
    @classmethod
    def random(cls, full_grid):
        # Read values from config file
        with open("./Objects/config/RandomWalk.yaml", 'r') as stream:
            data_loaded = yaml.safe_load(stream)
        min_num_tentacles = data_loaded["Octopus"]["min_num_tentacles"]
        max_num_tentacles = data_loaded["Octopus"]["max_num_tentacles"]

        num_tentacles = random.randrange(min_num_tentacles,
            max_num_tentacles, 1)
        return cls(full_grid, num_tentacles)

    def _allowed_point(self, new_point, all_points):
        # Don't repeat ourselves
        if all_points.count(new_point) > 0:
            return False

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
            if (self.shape.draw_grid[X][Y][Z] 
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
        if int(len(_path)/2) <= self.min_tentacle_length/2:
            return []
        self.tentacle_length = random.randrange(self.min_tentacle_length/2, 
            int(len(_path)/2), 1)

        path = copy.copy(_path)
        
        # This is the path we choose a point from
        # It has the first and last taken out
        choice_path = copy.copy(_path)
        choice_path.pop(0)
        choice_path.pop(len(choice_path)-1)
        
        new_path = []
        while not new_path:
            path = copy.copy(_path)
            start = random.choice(choice_path)
            
            # Remove this point and adjacent points so we can
            # do intersect or touch properly
            index = path.index(start)
            before = path.pop(index-1)
            # The index has changed because we just popped
            # Go back one for all
            after = path.pop(index)
            self.grid[start[0]][start[1]][start[2]] = False
            self.grid[before[0]][before[1]][before[2]] = False
            self.grid[after[0]][after[1]][after[2]] = False
            
            directions = [[1,0,0],[0,1,0],[0,0,1],[-1,0,0],[0,-1,0],[0,0,-1]]
            for direction in directions:
                try:    # skip if this is out of bounds     
                    start_path = list(map(add, 
                                    direction, 
                                    start))
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
