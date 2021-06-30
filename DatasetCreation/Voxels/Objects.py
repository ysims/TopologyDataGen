import numpy as np
import itertools
import random
import math
from operator import add

from Geometry import rotate_grid, distance3d, intersect_or_touch

class Sphere(object): 
    # center: center of the sphere
    # radius: radius of the sphere
    # size: how big the voxel grid is
    def __init__(self, full_grid, center, radius, size):
        # Set sphere information
        self.center = center
        self.radius = radius
        self.true_radius = 0
        self.full_grid = full_grid
        
        # Create a sphere as best we can with these parameters
        x, y, z = np.indices((size, size, size))
        self.grid = (x > size)   # False grid
        self.grid[center[0], center[1], center[2]] = True   # Add the center to the grid
        
        # Add all possible movement directions
        movement_direction = [] # list of value movements
        for x,y,z in itertools.permutations([1,0,0],3):
            movement_direction.append([x,y,z])
            movement_direction.append([-x,-y,-z])       
        movement_direction.sort()
        movement_direction = list(movement_direction for movement_direction,_ in itertools.groupby(movement_direction)) # remove duplicates

        self.recurse_sphere(movement_direction, center)
        print("The true radius is ", self.true_radius, ", compared with requested ", self.radius)

    # Make a random sphere
    @classmethod
    def random(cls, grid, size):
        center = [random.randrange(1, size-1, 1), random.randrange(1, size-1, 1), random.randrange(1, size-1, 1)]
        radius = random.randrange(3, int(size/6), 1)
        center = [15,15,15]
        radius = 6
        return cls(grid, center, radius, size)

    # Recursive function to add points to the sphere until it satisfies the conditions
    def recurse_sphere(self, movement_direction, current):
        # Update the true radius
        if self.true_radius < distance3d(self.center, current):
            self.true_radius = distance3d(self.center, current)
                
        # Recurse and add all points around this point
        for movement in movement_direction:
            
            point = [current[0] + movement[0], current[1] + movement[1], current[2] + movement[2]]

            # We don't want to recurse on this point if we've already done it before
            if self.grid[point[0]][point[1]][point[2]]:
                continue
            
            # Check that we've not exceeded the requested radius of the sphere
            if distance3d(self.center, point) > self.radius:
                continue  # we don't want to continue in this state

            # Make sure this doesn't intersect or touch something
            if intersect_or_touch(point, self.full_grid):
                continue # don't want to continue in this state
            
            # Add the point and recurse on it if it passes the tests
            self.grid[point[0]][point[1]][point[2]] = True
            self.recurse_sphere(movement_direction, point)



class Torus(object):
    # Make a specific torus
    def __init__(self, center, major_radius, minor_radius, minor_amplitude, rotation, size):
        # Set torus information
        self.center = center
        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.rotation = rotation
        self.size = size

        # Make a rotated grid and use it to make a voxelised torus
        x,y,z = rotate_grid(size, rotation, center)
        self.grid = pow(np.sqrt((x - center[0])**2 + (y - center[1])**2) - major_radius, 2) + (z - center[2])**2 <= \
            minor_radius ** 2 + minor_amplitude * (np.sin(x) + np.sin(y))

    # Make a random torus
    @classmethod
    def random(cls, size):
        rotation = [random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi)]
        center = [random.randrange(1, size-1, 1), random.randrange(1, size-1, 1), random.randrange(1, size-1, 1)]
        major_radius = random.randrange(4, int(size/6), 1)
        minor_radius = random.randrange(2, major_radius-1, 1)
        minor_amplitude = random.randrange(0, max(1,int(minor_radius/2)), 2)
        return cls(center, major_radius, minor_radius, minor_amplitude, rotation, size)

    # This will get the circle that 'plugs' up the torus, to prevent tunnels going through
    def get_disc(self):
        x,y,z = rotate_grid(self.size, self.rotation, self.center)
        return (z > self.center[2]-1) & (z < self.center[2] + 1) & ((x - self.center[0])**2 + (y - self.center[1])**2 <= self.major_radius ** 2)

# A 2-torus
class Torus2(object):
    # Make a specific torus
    def __init__(self, center, major_radius, minor_radius, minor_amplitude, rotation, size):
        # Set torus information
        self.center = center
        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.rotation = rotation
        self.size = size

        # Make a rotated grid and use it to make a voxelised torus
        x,y,z = rotate_grid(size, rotation, center)
        torus1 = pow(np.sqrt((x - center[0])**2 + (y - center[1])**2) - major_radius, 2) + (z - center[2])**2 <= \
            minor_radius ** 2 + minor_amplitude * (np.sin(x) + np.sin(y))
        torus2 = pow(np.sqrt((x - center[0] + major_radius*2)**2 + (y - center[1])**2) - major_radius, 2) + (z - center[2])**2 <= \
            minor_radius ** 2 + minor_amplitude * (np.sin(x) + np.sin(y))
        self.grid = torus1 | torus2

    # Make a random torus
    @classmethod
    def random(cls, size):
        rotation = [random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi)]
        center = [random.randrange(1, size-1, 1), random.randrange(1, size-1, 1), random.randrange(1, size-1, 1)]
        major_radius = random.randrange(4, int(size/6), 1)
        minor_radius = random.randrange(2, major_radius-1, 1)
        minor_amplitude = random.randrange(0, max(1,int(minor_radius/2)), 2)
        return cls(center, major_radius, minor_radius, minor_amplitude, rotation, size)

    # This will get the circle that 'plugs' up the torus, to prevent tunnels going through
    def get_disc(self):
        x,y,z = rotate_grid(self.size, self.rotation, self.center)
        disc1 = (z > self.center[2]-1) & (z < self.center[2] + 1) & ((x - self.center[0])**2 + (y - self.center[1])**2 <= self.major_radius ** 2)
        disc2 = (z > self.center[2]-1) & (z < self.center[2] + 1) & ((x - self.center[0] + self.major_radius * 2)**2 + (y - self.center[1])**2 <= self.major_radius ** 2)
        return disc1 | disc2

# This object represents a sphere with a sphere-shaped hole inside it
class Island(object):
    # center: center of the island
    # outer radius: radius of the outer sphere
    # inner radius: radius of the inner sphere
    # outer amplitude: how much 'wiggle' to add to the outer sphere
    # inner amplitude: how much 'wiggle' to add to the inner sphere
    # rotation: a list of three rotations that are x,y,z axis rotations and rotated in that order
    # size: how big the voxel grid is
    def __init__(self, center, outer_radius, inner_radius, outer_amplitude, inner_amplitude, rotation, size):
        # Set sphere information
        self.center = center
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.outer_amplitude = outer_amplitude
        self.inner_amplitude = inner_amplitude
        self.rotation = rotation

        # Make a rotated grid and use it to make a voxelised sphere with a hole in the middle (island)
        x,y,z = rotate_grid(size, rotation, center)
        self.grid = ((pow(x - center[0], 2) + pow(y - center[1], 2) + pow(z - center[2], 2)) <= outer_radius ** 2 + outer_amplitude * (np.sin(x) + np.sin(y))) \
            & ((pow(x - center[0], 2) + pow(y - center[1], 2) + pow(z - center[2], 2)) >= inner_radius ** 2 + (inner_amplitude * np.sin(x) + np.sin(y)))

    # Make a random island
    @classmethod
    def random(cls, size):
        rotation = [random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi)]
        center = [random.randrange(1, size-1, 1), random.randrange(1, size-1, 1), random.randrange(1, size-1, 1)]
        outer_radius = random.randrange(4, int(size/6), 1)
        inner_radius = random.randrange(2, outer_radius-1, 1)
        outer_amplitude = random.randrange(0, inner_radius - 1, 1)
        inner_amplitude = random.randrange(0, int(inner_radius/2), 1)
        return cls(center, outer_radius, inner_radius, outer_amplitude, inner_amplitude, rotation, size)

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

        # Add all possible movement directions
        movement_direction = [] # list of value movements
        for x,y,z in itertools.permutations([1,0,0],3):
            movement_direction.append([x,y,z])
            movement_direction.append([-x,-y,-z])       
        movement_direction.sort()
        movement_direction = list(movement_direction for movement_direction,_ in itertools.groupby(movement_direction)) # remove duplicates

        while ((not border[current_point[0]][current_point[1]][current_point[2]]) or current_point==start):
            point_added = False
            random.shuffle(movement_direction) # shuffle so we don't always go the same way
            for direction in movement_direction:
                if not self.tunnel_intersect(grid, list(map(add, direction, current_point)), objects):
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

    def tunnel_intersect(self, grid, point, objects):
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

    # Make a random tunnel
    @classmethod
    def random(cls, size, objects, border):
        # Create a random start position on a face
        start = [random.randrange(2,size-2,1) for i in range(0,3)]
        start[random.randrange(0,3,1)] = 0 if random.randrange(0,2,1) == 0 else size-1
        return cls(start, size, objects, border)
