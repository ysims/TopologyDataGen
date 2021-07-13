import copy
import itertools
import numpy as np
from operator import add
import random

from Geometry import surrounded


class Tunnel(object):
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

        # Make a grid with just this starting point
        size = full_grid[0][0].size
        x,y,z = np.indices((size, size, size))
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
