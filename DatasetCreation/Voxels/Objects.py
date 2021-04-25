import numpy as np
import itertools
import random
import math
from operator import add

from Geometry import rotate_grid


class Circle: 
    # center: center of the circle
    # radius: radius of the circle
    # amplitude: how much 'wiggle' to add to the circle
    # rotation: a list of three rotations that are x,y,z axis rotations and rotated in that order
    # size: how big the voxel grid is
    def __init__(self, center, radius, amplitude, rotation, size):
        # Set circle information
        self.center = center
        self.radius = radius
        self.rotation = rotation
        self.amplitude = amplitude

        # Make a rotated grid and use it to make a voxelised circle
        x,y,z = rotate_grid(size, rotation, center)
        self.grid = (pow(x - center[0], 2) + pow(y - center[1], 2) + pow(z - center[2], 2)) <= radius ** 2 + (amplitude * np.sin(x)) ** 2 + (amplitude * np.sin(y)) ** 2

    # Make a random circle
    @classmethod
    def random(cls, size):
        rotation = [random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi)]
        center = [random.randrange(1, size-1, 1), random.randrange(1, size-1, 1), random.randrange(1, size-1, 1)]
        radius = random.randrange(2, int(size/6), 1)
        amplitude = random.randrange(0, int(radius/2), 1)
        return cls(center, radius, amplitude, rotation, size)


class Torus(object):
    # Make a specific torus
    def __init__(self, center, major_radius, minor_radius, rotation, size):
        # Set torus information
        self.center = center
        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.rotation = rotation
        
        # Make a rotated grid and use it to make a voxelised torus
        x,y,z = rotate_grid(size, rotation, center)
        self.grid = pow((np.sqrt(pow((x - center[0]),2) + pow(y - center[1],2)) - major_radius), 2) + pow(z - center[2], 2) <= pow(minor_radius,2)

    # Make a random torus
    @classmethod
    def random(cls, size):
        rotation = [random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi)]
        center = [random.randrange(1, size-1, 1), random.randrange(1, size-1, 1), random.randrange(1, size-1, 1)]
        major_radius = random.randrange(3, int(size/6), 1)
        minor_radius = random.randrange(2, major_radius, 1)
        return cls(center, major_radius, minor_radius, rotation, size)

class Line:
    # Parameters
    # start: coordinate where the line starts
    # size: size of the voxel grid
    # objects: list of objects for the line to avoid
    # Description
    # Given a starting position on the border, make a line from this point to some other point on the border 
    # Any border point should not intersect with an object since object cannot be on the border
    def __init__(self, start, size, objects, border):
        # Make a grid with just this starting point
        x, y, z = np.indices((size, size, size))
        grid = (x==start[0]) & (y==start[1]) & (z==start[2])
        current_point = start
        
        # Find the forward direction
        forward = [0,0,0]
        for i in range(len(current_point)):
            if current_point[i] == 0:
                forward[i] = 1
            elif current_point[i] == size-1:
                forward[i] = -1

        # Add all possible movement directions
        movement_direction = [] # list of value movements
        for x,y,z in itertools.permutations([1,0,0],3):
            if [x,y,z] != [ -a for a in forward]:   # we don't want to add if it's backwards
                movement_direction.append([x,y,z])
            if [-x,-y,-z] != [ -a for a in forward]:   # do the negation as well
                movement_direction.append([-x,-y,-z])       
        movement_direction.sort()
        movement_direction = list(movement_direction for movement_direction,_ in itertools.groupby(movement_direction)) # remove duplicates
        # Remove one direction so that we don't risk making a loop without knowing - but don't remove the forward direction
        movement_direction.remove(movement_direction[0] if movement_direction[0] != forward else movement_direction[1])

        # Go forward before doing anything else
        current_point = list(map(add, forward, current_point))
        grid[current_point[0]][current_point[1]][current_point[2]] = True

        while ((not border[current_point[0]][current_point[1]][current_point[2]]) or current_point==start):
            point_added = False
            random.shuffle(movement_direction) # shuffle so we don't always go the same way
            for direction in movement_direction:
                if not self.line_intersect(grid, list(map(add, direction, current_point)), objects):
                    current_point = list(map(add, direction, current_point))
                    grid[current_point[0]][current_point[1]][current_point[2]] = True
                    point_added = True
                    break
            # We've reached a point where nowhere will work!
            if not point_added:
                self.valid = False
        self.valid = True
        self.grid = grid

    def line_intersect(self, grid, point, objects):
        # Check if we can even move to this point
        if grid[point[0]][point[1]][point[2]]:
            return True

        # Check if there are any objects around this point
        for x,y,z in itertools.product([-1,0,1],repeat=3):
            try:    # skip if this is out of bounds
                if objects[point[0] + x][point[1] + y][point[2] + z]:
                    return True
            except:
                continue
        return False

    # Make a random line
    @classmethod
    def random(cls, size, objects, border):
        # Create a random start position on a face
        start = [random.randrange(2,size-2,1) for i in range(0,3)]
        start[random.randrange(0,3,1)] = 0 if random.randrange(0,2,1) == 0 else size-1
        return cls(start, size, objects, border)
