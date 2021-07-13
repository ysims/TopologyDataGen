import numpy as np
import itertools
import random
import math
from operator import add
import copy
import scipy.ndimage

from Geometry import rotate_grid, distance3d, intersect_or_touch, surrounded, rotate_object

class Tunnel(object):
    # Parameters
    # start: coordinate where the tunnel starts
    # size: size of the voxel grid
    # objects: list of objects for the tunnel to avoid
    # Description
    # Given a starting position on the border, make a tunnel from this point to some other point on the border 
    # Any border point should not intersect with an object since object cannot be on the border
    def __init__(self, start, size, objects, border):
        # Make a grid with just this starting point
        x, y, z = np.indices((size, size, size))
        grid = (x > size)   # False grid
        current_point = start
        # Find the forward direction
        forward = [0,0,0]
        for i in range(len(current_point)):
            if current_point[i] == 0:
                forward[i] = 1
            elif current_point[i] == size-1:
                forward[i] = -1

        # Add forward point
        previous_point = current_point
        current_point = list(map(add, forward, current_point))
        grid[current_point[0]][current_point[1]][current_point[2]] = True

        # Add all possible movement directions
        movement_direction = [] # list of value movements
        for x,y,z in itertools.permutations([1,0,0],3):
            movement_direction.append([x,y,z])
            movement_direction.append([-x,-y,-z])       
        movement_direction.sort()
        movement_direction = list(movement_direction for movement_direction,_ in itertools.groupby(movement_direction)) # remove duplicates

        # Loop while we've not hit the border
        while (not border[current_point[0]][current_point[1]][current_point[2]]):
            point_added = False
            random.shuffle(movement_direction) # shuffle so we don't always go the same way
            for direction in movement_direction:
                if not self.tunnel_intersect(copy.copy(grid), list(map(add, direction, current_point)), current_point, previous_point, objects):
                    previous_point = current_point
                    current_point = list(map(add, direction, current_point))
                    grid[current_point[0]][current_point[1]][current_point[2]] = True
                    point_added = True
                    break
            # We've reached a point where nowhere will work!
            if not point_added:
                self.valid = False
                return
        self.valid = True
        self.grid = grid

    def tunnel_intersect(self, grid, new_point, old_point, old_old_point, objects):
        # Check if we can even move to this point
        # old_point was already checked last time, so should be good
        # This will stop us going back on ourselves as well, ie old == new
        try:
            if grid[new_point[0]][new_point[1]][new_point[2]]:
                return True
        except:
            return True

        # We will always be accused of touching the grid if the previous point is there
        grid[old_point[0]][old_point[1]][old_point[2]] = False
        grid[old_old_point[0]][old_old_point[1]][old_old_point[2]] = False

        # Check if there are any objects around this point
        for x,y,z in itertools.product([-1,0,1],repeat=3):
            try:    # skip if this is out of bounds
                # Check if there are other objects around
                if objects[new_point[0] + x][new_point[1] + y][new_point[2] + z]:
                    return True
                # Check if we're about to loop back on ourselves
                if grid[new_point[0] + x][new_point[1] + y][new_point[2] + z]:
                    return True
            except:
                continue
        return False

    # Make a random tunnel
    @classmethod
    def random(cls, size, objects, border):
        # Create a random start position on a face
        start = [random.randrange(2,size-2,1) for i in range(0,3)]
        start[random.randrange(0,3,1)] = 0 if random.randrange(0,2,1) == 0 else size-1
        return cls(start, size, objects, border)

# -------- I don't know what this is - sphere with tunnels coming off it ------------
class Tentacle(object):
    def __init__(self, grid, size, num_tentacles):
        self.sphere = Sphere.random(grid, size)
        while not self.sphere.valid:
            self.sphere = Sphere.random(grid, size)
        self.grid = self.sphere.grid
        self.full_grid = grid
        self.size = size
        self.num_tentacles = num_tentacles
        self.valid = True

        # Add the number of tentacles that we want
        # Retry if it fails
        for _ in range(num_tentacles):
            while not self.make_tentacle():
                continue

    # Make a random octopus!
    @classmethod
    def random(cls, grid, size):
        # Create a random start position on a face
        num_tentacles = random.randrange(10,30)
        return cls(grid, size, num_tentacles)

    def get_edges(self):
        # We will make a 'tentacle' going off from one of the edges
        edges = []
        for X,Y,Z in itertools.product(range(0, self.size), repeat=3):
            if self.sphere.grid[X][Y][Z]:
                directions = [[1,0,0],[0,1,0],[0,0,1],[-1,0,0],[0,-1,0],[0,0,-1]]   # lets not go diagonal
                for direction in directions:
                    try:    # skip if this is out of bounds
                        if not self.grid[X + direction[0]][Y + direction[1]][Z + direction[2]]:  # if it's empty, we're not surrounded
                            edges.append([X,Y,Z])   # is an edge if it's a sphere point and isn't surrounded by other sphere points
                    except:
                        continue

        if not edges:
            print("No edges, something is wrong")
            self.valid = False

        return edges


    # We want to make a tentacle that doesn't touch anything, including the boundary
    # It can branch if it wants to
    def make_tentacle(self):
        # Find the edges and chose a random point
        edges = self.get_edges()
        point = random.choice(edges)

        all_points = [] # We want to keep track of all the points in the tunnel
        for x,y,z in itertools.product([-1,0,1],repeat=3):
            try:    # skip if this is out of bounds
                if not self.grid[point[0] + x][point[1] + y][point[2] + z]:
                    all_points.append([point[0] + x, point[1] + y, point[2] + z])
                    break   # We've found something, so don't keep looking
            except:
                continue

        # If we didn't get anything, then there's no way to make a tunnel from this edge
        if not all_points:
            print("Something went wrong.")
            return False

        # Add all possible movement directions
        movement_direction = [] # list of value movements
        for x,y,z in itertools.permutations([1,0,0],3):
            movement_direction.append([x,y,z])
            movement_direction.append([-x,-y,-z])       
        movement_direction.sort()
        movement_direction = list(movement_direction for movement_direction,_ in itertools.groupby(movement_direction)) # remove duplicates

        # Lets put a random limit on the length of the tentacle
        # TODO: hardcoded values ew
        length = random.randrange(20, 50, 1)
        
        while len(all_points) < length:
            point_added = False
            random.shuffle(movement_direction) # shuffle so we don't always go the same way
            for direction in movement_direction:
                new_point = list(map(add, direction, all_points[len(all_points) - 1]))
                # If we don't intersect or touch anything, then move here
                if not intersect_or_touch(new_point, (self.grid | self.full_grid)):
                    # new_point is now a valid point in the tunnel
                    all_points.append(new_point)
                    # We want to add onto the grid the point from two runs ago
                    if len(all_points) > 2:
                        to_add = all_points[len(all_points) - 3]
                        self.grid[to_add[0], to_add[1], to_add[2]] = True
                    point_added = True
                    break   # Don't keep going with the for loop
            
            if not point_added:
                # If we get to this point, we weren't able to move
                # See if this was a decent enough try, otherwise just return false
                if (len(all_points) < 15):
                    # Remove anything we added because we don't want it anymore
                    for point in all_points:
                        self.grid[point[0], point[1], point[2]] = False
                    return False
                
                # Still need to break from the while loop
                else:
                    break
        
        # The last two points won't be there, so just add everything in our tunnel to the grid
        for point in all_points:
            self.grid[point[0], point[1], point[2]] = True

        return True     # nothing seemed to go wrong so return true
