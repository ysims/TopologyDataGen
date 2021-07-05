import numpy as np
import itertools
import random
import math
from operator import add
import copy
import scipy.ndimage

from Geometry import rotate_grid, distance3d, intersect_or_touch

class Sphere(object): 

    # center: center of the sphere
    # radius: radius of the sphere
    # size: how big the voxel grid is
    def __init__(self, full_grid, center, radius, size):
        # Check we're not starting in an invalid location
        if intersect_or_touch(center, full_grid):
            self.valid = False
            return

        # Set sphere information
        self.center = center
        self.radius = radius
        self.full_grid = full_grid
        self.valid = True
        self.size = size
        
        self.create_sphere()
        print("Made a sphere")

    # Make a random sphere
    @classmethod
    def random(cls, grid, size):
        center = (random.randrange(5, size-5, 1), random.randrange(5, size-5, 1), random.randrange(5, size-5, 1))
        radius = random.randrange(3, 6, 1)
        return cls(grid, center, radius, size)

    # Create a sphere and if it touches or intersects something, move it away
    def create_sphere(self):
        dilation_structure = scipy.ndimage.generate_binary_structure(3, 3)
        # Create a sphere and move it if needed
        x, y, z = np.indices((self.size, self.size, self.size))
        self.grid = (pow(x - self.center[0],2) + pow(y - self.center[1],2) + pow(z - self.center[2], 2)) < pow(self.radius, 2)

        # Get the intersection of the sphere (dilated to take into account touching) and other objects to see if there's any intersection/touching
        intersection = scipy.ndimage.binary_dilation(self.grid, dilation_structure, 1) & self.full_grid

        # If there is a true point, find it
        intersecting_vector = None
        for X,Y,Z in itertools.product(range(0, self.size), repeat=3):
            if (intersection[X][Y][Z]):
                intersecting_vector = [self.center[0] - X, self.center[1] - Y, self.center[2] - Z]
                break
        
        # If it's not none, then we found something
        # Keep looping until we don't intersect
        count_max = 100   # maximum times we'll try moving
        count = 0         # times we've tried
        while intersecting_vector is not None:
            # Check if we've tried too many times
            count += 1
            if count is count_max:
                print("Too hard.")
                self.valid = False
                break

            self.center = [self.center[0] + intersecting_vector[0], self.center[1] + intersecting_vector[1], self.center[2] + intersecting_vector[2]]
            self.grid = (pow(x - self.center[0],2) + pow(y - self.center[1],2) + pow(z - self.center[2], 2)) < pow(self.radius, 2)

            # Get the intersection of the sphere (dilated to take into account touching) and other objects to see if there's any intersection/touching
            intersection = scipy.ndimage.binary_dilation(self.grid, dilation_structure, 1) & self.full_grid

            # If there is a true point, find it
            intersecting_vector = None
            for X,Y,Z in itertools.product(range(0, self.size), repeat=3):
                if (intersection[X][Y][Z]):
                    intersecting_vector = [self.center[0] - X, self.center[1] - Y, self.center[2] - Z]
                    break

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

    # def create_torus(self, ):


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
                    print("added ", current_point)
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
