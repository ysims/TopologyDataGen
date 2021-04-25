import numpy as np
import math
import itertools
import random
import scipy.ndimage
from operator import add

# General function for creating a homogeneous transformation matrix made up of X-Y-Z rotations
# rotation is a 3d array of x rotation, y rotation, z rotation applied that order.
def get_rotation(rotation):
    X = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, np.cos(rotation[0]), np.sin(rotation[0]), 0.0], [0.0, -np.sin(rotation[0]), np.cos(rotation[0]), 0.0], [0.0, 0.0, 0.0, 1.0]])
    Y = np.array([[np.cos(rotation[1]), 0.0, -np.sin(rotation[1]), 0.0], [0.0, 1.0, 0.0, 0.0], [np.sin(rotation[1]), 0.0, np.cos(rotation[1]), 0.0], [0.0, 0.0, 0.0, 1.0]])
    Z = np.array([[np.cos(rotation[2]), np.sin(rotation[2]), 0.0, 0.0], [-np.sin(rotation[2]), np.cos(rotation[2]), 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
    return Z.dot(Y.dot(X))

# rotation is a 3d array of x rotation, y rotation, z rotation applied that order.
# C is the center about which we want to rotate - in most cases, the center of the shape we are rotating
# P is a point x,y,z which we are rotating about the center by the angled defined in rotation
def rotate(rotation, C, P):
    # Homogeneous transformation with the rotational component
    R = get_rotation(rotation)
    # Homogeneous transformation matrices with the negative center and positive center
    T_neg = np.array([[1.0, 0.0, 0.0, -C[0]], [0.0, 1.0, 0.0, -C[1]], [0.0, 0.0, 1.0, -C[2]], [0.0, 0.0, 0.0, 1.0]])
    T_pos = np.array([[1.0, 0.0, 0.0, C[0]], [0.0, 1.0, 0.0, C[1]], [0.0, 0.0, 1.0, C[2]], [0.0, 0.0, 0.0, 1.0]])
    # Turn the point into a form we can multiply with
    P_full = [P[0], P[1], P[2], 1.0]
    # Return C*R*-C*P - move the origin to the center, rotate the point, then move the origin back
    return T_pos.dot(R.dot(T_neg.dot(P_full)))[:3]


# Class that holds one object with cavities in it, of various shapes.
class Voxels3d:
    # Constructor
    def __init__(self, size):
        self.size = size # this should be a 3d array of lengths in the x,y,z directions of our space
        self.objects = [] # initialise our array of objects
        # Create the full shape everything is contained in. True areas are the border and false are the insides
        x, y, z = np.indices((self.size[0], self.size[1], self.size[2]))
        self.border = (x == 0) | (x == self.size[0] - 1) | (y == 0) | (y == self.size[1] - 1) | (z == 0) | (z == self.size[2] - 1) # lets use a cube

    # --------------------------------------------------------------------------------------------
    # Create and return objects, to be used by the add<Object> functions
    # This will create a wavy circle and return it
    def get_wavy_circle(self, center, radius, rotation):
        x, y, z = np.indices((self.size[0], self.size[1], self.size[2]))
        for X,Y,Z in itertools.product(range(0, self.size[0]), repeat=3):
            x[X][Y][Z],y[X][Y][Z],z[X][Y][Z] = rotate(rotation, center, [X,Y,Z])

        wavy_circle = (pow(x - center[0], 2) + pow(y - center[1], 2) + pow(z - center[2], 2)) <= pow(radius+np.sin(x), 2)
        return wavy_circle

    def get_cube(self, center, length, rotation):
        x, y, z = np.indices((self.size[0], self.size[1], self.size[2]))
        for X,Y,Z in itertools.product(range(0, self.size[0]), repeat=3):
            x[X][Y][Z],y[X][Y][Z],z[X][Y][Z] = rotate(rotation, center, [X,Y,Z])
        if center[0] % 2 == 1:
            center[0] -= 1
            center[1] -= 1
            center[2] -= 1
        cube = ((center[0] - length/2 < x) & (x < center[0] + length/2)) & ((center[1] - length/2 < y) & (y < center[1] + length/2)) & ((center[2] - length/2 < z) & (z < center[2] + length/2))
        return cube

    # This will create a circle and return it
    def get_circle(self, center, radius, rotation):
        x, y, z = np.indices((self.size[0], self.size[1], self.size[2]))
        for X,Y,Z in itertools.product(range(0, self.size[0]), repeat=3):
            x[X][Y][Z],y[X][Y][Z],z[X][Y][Z] = rotate(rotation, center, [X,Y,Z])

        circle = (pow(x - center[0],2) + pow(y - center[1],2) + pow(z - center[2], 2)) <= pow(radius, 2)
        return circle

    # This will create a torus and return it
    def get_torus(self, center, major_radius, minor_radius, rotation):
        x, y, z = np.indices((self.size[0], self.size[1], self.size[2]))
        for X,Y,Z in itertools.product(range(0, self.size[0]), repeat=3):
            x[X][Y][Z],y[X][Y][Z],z[X][Y][Z] = rotate(rotation, center, [X,Y,Z])

        torus = pow((np.sqrt(pow((x - center[0]),2) + pow(y - center[1],2)) - major_radius), 2) + pow(z - center[2], 2) <= pow(minor_radius,2)
        return torus
    # --------------------------------------------------------------------------------------------
    
    # Given an object, check if it intersects with existing objects
    def check_intersect(self, new_object):
        if (new_object & self.border).any():
            return True

        for object in self.objects:
            if (object & new_object).any():
                return True
        return False

    # --------------------------------------------------------------------------------------------
    # The following functions will add objects if there are no intersections with existing objects
    def add_torus(self, center, major_radius, minor_radius, rotation):
        torus = self.get_torus(center, major_radius, minor_radius, rotation)
        torus_dilation = scipy.ndimage.binary_dilation(torus,iterations=2)
        if self.check_intersect(torus_dilation):
            return False
        self.objects.append(torus)
        return True

    def add_circle(self, center, radius, rotation):
        circle = self.get_circle(center, radius, rotation)
        circle_dilation = scipy.ndimage.binary_dilation(circle,iterations=2)
        if self.check_intersect(circle_dilation):
            return False
        self.objects.append(circle)
        return True

    def add_wavy_circle(self, center, radius, rotation):
        wavy_circle = self.get_wavy_circle(center, radius, rotation)
        wavy_circle_dilation = scipy.ndimage.binary_dilation(wavy_circle,iterations=2)
        if self.check_intersect(wavy_circle_dilation):
            return False
        self.objects.append(wavy_circle)
        return True

    # Given a starting position on the border, make a line from this point to some other point on the border 
    # Any border point should not intersect with an object since object cannot be on the border
    def add_line(self, start):
        x, y, z = np.indices((self.size[0], self.size[1], self.size[2]))
        grid = (x==start[0]) & (y==start[1]) & (z==start[2])

        current_point = start
        movement_direction = [] # array of value movements
        first_direction = [0,0,0]

        # If we don't start on a particular face, we can move towards it
        if current_point[0] != 0:
            movement_direction.append([-1,0,0])
        else:
            first_direction = [1,0,0]

        if current_point[0] != 29:
            movement_direction.append([1,0,0])
        else:
            first_direction = [-1,0,0]
        
        if current_point[1] != 0:
            movement_direction.append([0,-1,0])
        else:
            first_direction = [0,1,0]
        
        if current_point[1] != 29:
            movement_direction.append([0,1,0])
        else:
            first_direction = [0,-1,0]
        
        if current_point[2] != 0:
            movement_direction.append([0,0,-1])
        else:
            first_direction = [0,0,1]
        
        if current_point[2] != 29:
            movement_direction.append([0,0,1])
        else:
            first_direction = [0,0,-1]

        current_point = list(map(add, first_direction, current_point))
        grid[current_point[0]][current_point[1]][current_point[2]] = True
        
        if movement_direction[0] != first_direction:
            movement_direction.remove(movement_direction[0])
        else:
            movement_direction.remove(movement_direction[1])

        random.shuffle(movement_direction) # shuffle so we don't always go the same way

        while ((not self.border[current_point[0]][current_point[1]][current_point[2]]) or current_point==start):
            point_added = False
            random.shuffle(movement_direction) # shuffle so we don't always go the same way
            for direction in movement_direction:
                if not self.line_intersect(grid, list(map(add, direction, current_point))):
                    current_point = list(map(add, direction, current_point))
                    grid[current_point[0]][current_point[1]][current_point[2]] = True
                    point_added = True
                    break
            # We've reached a point where no where will work!
            if not point_added:
                return False
        self.objects.append(grid)
        return True

    def line_intersect(self, grid, point):
        # Check if we can even move to this point
        if grid[point[0]][point[1]][point[2]]:
            return True

        # Check if there are any objects around this point
        objects = self.get_objects()
        for x,y,z in itertools.product([-1,0,1],repeat=3):
            try:    # skip if this is out of bounds
                if objects[point[0] + x][point[1] + y][point[2] + z]:
                    return True
            except:
                continue
        return False

    # --------------------------------------------------------------------------------------------
    # Add num_object number of objects randomly
    def add_objects(self, num_objects, num_lines):
        count = 0
        while count < num_objects: 
            if(self.add_random()):
                print("Success!")
                count += 1
        count = 0
        while count < num_lines:
            start = [random.randrange(2,self.size[0]-2,1) for i in range(0,3)]
            start[random.randrange(0,3,1)] = 0 if random.randrange(0,2,1) == 0 else self.size[0]-1
            if(self.add_line(start)):
                count += 1

    def add_random(self):
        # Make a random rotation
        rotation = [random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi)]
        # Make a random center (might as well not add in edges, they'll be boundary points)
        center = [random.randrange(1, self.size[0]-1, 1), random.randrange(1, self.size[1]-1, 1), random.randrange(1, self.size[2]-1, 1)]
        # Everything has some sort of outer radius, lets find it
        outer_radius = random.randrange(3, int(min(self.size)/6), 1)
        # We're gonna choose a shape randomly. There are three at the moment, so lets get [0-2] randomly
        shape = random.randrange(0, 3, 1)
        # Circle
        if shape == 0:
            print("Circle")
            return self.add_circle(center, outer_radius, rotation)
        elif shape == 1:
            print("Wavy circle")
            return self.add_wavy_circle(center, outer_radius, rotation)
        else:
            print("Torus")
            return self.add_torus(center, outer_radius, random.randrange(2, outer_radius, 1), rotation)

    # Get all the 'holes' as solid objects
    def get_objects(self):
        # Make a full false grid
        x, y, z = np.indices((self.size[0], self.size[1], self.size[2]))
        grid = x + y + z < 0
        # Loop over all objects and add them to the voxel grid 
        for object in self.objects:
            grid = grid | object
        return grid

    def get_full_objects(self):
        final = self.border
        for object in self.objects:
            final = final | object
        return ~final