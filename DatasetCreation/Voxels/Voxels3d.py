import numpy as np
import math
import itertools
import random
import scipy.ndimage

# General function for creating a homogeneous transformation matrix made up of X-Y-Z rotations
# rotation is a 3d array of x rotation, y rotation, z rotation applied that order.
def get_rotation(rotation):
    X = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, np.cos(rotation[0]), -np.sin(rotation[0]), 0.0], [0.0, np.sin(rotation[0]), np.cos(rotation[0]), 0.0], [0.0, 0.0, 0.0, 1.0]])
    Y = np.array([[np.cos(rotation[1]), 0.0, np.sin(rotation[1]), 0.0], [0.0, 1.0, 0.0, 0.0], [-np.sin(rotation[1]), 0.0, np.cos(rotation[1]), 0.0], [0.0, 0.0, 0.0, 1.0]])
    Z = np.array([[np.cos(rotation[2]), -np.sin(rotation[2]), 0.0, 0.0], [np.sin(rotation[2]), -np.cos(rotation[2]), 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
    return Z.dot(Y.dot(X))

# rotation is a 3d array of x rotation, y rotation, z rotation applied that order.
# C is the center about which we want to rotate - in most cases, the center of the shape we are rotating
# P is a point x,y,z which we are rotating about the center by the angled defined in rotation
def rotate(rotation, C, P):
    # Homogeneous transformation with the rotational component
    R = getRotation(rotation)
    # Homogeneous transformation matrices with the negative center and positive center
    T_neg = np.array([[1.0, 0.0, 0.0, -C[0]], [0.0, 1.0, 0.0, -C[1]], [0.0, 0.0, 1.0, -C[2]], [0.0, 0.0, 0.0, 1.0]])
    T_pos = np.array([[1.0, 0.0, 0.0, C[0]], [0.0, 1.0, 0.0, C[1]], [0.0, 0.0, 1.0, C[2]], [0.0, 0.0, 0.0, 1.0]])
    # Turn the point into a form we can multiply with
    P_full = [P[0], P[1], P[2], 1.0]
    # Return C*R*-C*P - move the origin to the center, rotate the point, then move the origin back
    return T_pos.dot(R.dot(T_neg.dot(P_full)))

# Class that holds one object with cavities in it, of various shapes.
class Voxels3d:
    # Constructor
    def __init__(self, size):
        self.size = size # this should be a 3d array of lengths in the x,y,z directions of our space
        self.objects = [] # initialise our array of objects
        # Create the full shape everything is contained in. True areas are the border and false are the insides
        self.border = ~self.getCircle([size[0]/2, size[1]/2, size[2]/2], min(size)/2-1, [0,0,0]) # lets just use a circle for now

    # --------------------------------------------------------------------------------------------
    # Create and return objects, to be used by the add<Object> functions
    # This will create a wavy circle and return it
    def getWavyCircle(self, center, radius, rotation):
        x, y, z = np.indices((self.size[0], self.size[1], self.size[2]))
        for X,Y,Z in itertools.product(range(0, 30), repeat=3):
            x[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[0]
            y[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[1]
            z[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[2]
        wavyCircle = (pow(x - center[0], 2) + pow(y - center[1], 2) + pow(z - center[2], 2)) < pow(radius+np.sin(x), 2)
        return wavyCircle

    # This will create a circle and return it
    def getCircle(self, center, radius, rotation):
        x, y, z = np.indices((self.size[0], self.size[1], self.size[2]))
        for X,Y,Z in itertools.product(range(0, 30), repeat=3):
            x[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[0]
            y[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[1]
            z[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[2]
        circle = (pow(x - center[0],2) + pow(y - center[1],2) + pow(z - center[2], 2)) < pow(radius, 2)
        return circle

    # This will create a torus and return it
    def getTorus(self, center, major_radius, minor_radius, rotation):
        x, y, z = np.indices((self.size[0], self.size[1], self.size[2]))
        for X,Y,Z in itertools.product(range(0, 30), repeat=3):
            x[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[0]
            y[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[1]
            z[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[2]
        torus = pow((np.sqrt(pow((x - center[0]),2) + pow(y - center[1],2)) - major_radius), 2) + pow(z - center[2], 2) < pow(minor_radius,2)
        return torus
    # --------------------------------------------------------------------------------------------
    
    # Given an object, check if it intersects with existing objects
    def checkIntersect(self, new_object):
        intersect = new_object & self.border
        print(self.border)
        # Check boundary
        # if (new_object & self.border).any():
        #     return True
        # Check each object for an intersection with this one
        for object in self.objects:
            intersect = intersect & object
        if intersect.any():
            return True
        # Didn't find any intersection
        return False

    # --------------------------------------------------------------------------------------------
    # The following functions will add objects if there are no intersections with existing objects
    def addTorus(self, center, major_radius, minor_radius, rotation):
        if self.checkIntersect(self.getTorus(center, major_radius, minor_radius+1, rotation)):
            return False
        self.objects.append(self.getTorus(center, major_radius, minor_radius, rotation))
        return True

    def addCircle(self, center, radius, rotation):
        if self.checkIntersect(self.getCircle(center, radius+1, rotation)):
            return False
        self.objects.append(self.getCircle(center, radius, rotation))
        return True

    def addWavyCircle(self, center, radius, rotation):
        if self.checkIntersect(self.getWavyCircle(center, radius+1, rotation)):
            return False
        self.objects.append(self.getWavyCircle(center, radius, rotation))
        return True
    # --------------------------------------------------------------------------------------------
    # Add amount number of objects randomly
    def addObjects(self, amount):
        count = 0
        while count < amount: 
            if(self.addRandom()):
                count += 1
                print("Hit!!!!!!!!!!!!!!!!!!!!!!!!!")
            else:
                print("Miss...")

    def addRandom(self):
        # Make a random rotation
        rotation = [random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi)]
        # Make a random center (might as well not add in edges, they'll be boundary points)
        center = [random.randrange(1, self.size[0]-1, 1), random.randrange(1, self.size[1]-1, 1), random.randrange(1, self.size[2]-1, 1)]
        # Everything has some sort of outer radius, lets find it
        outer_radius = random.randrange(3, int(min(self.size)/4), 1)
        # We're gonna choose a shape randomly. There are three at the moment, so lets get [0-2] randomly
        shape = random.randrange(0, 3, 1)
        # Circle
        if shape == 0:
            print("Circle!")
            return self.addCircle(center, outer_radius, rotation)
        elif shape == 1:
            print("Wavy circle!")
            return self.addWavyCircle(center, outer_radius, rotation)
        else:
            print("Torus!")
            return self.addTorus(center, outer_radius, random.randrange(2, outer_radius, 1), rotation)

    def getObjects(self):
        # make a full false grid
        x, y, z = np.indices((self.size[0], self.size[1], self.size[2]))
        first = x + y + z < 0
        for object in self.objects:
            first = first | object
        return first

    def getFullObjects(self):
        final = self.border
        for object in self.objects:
            final = final | object
        return ~final

    def checkIntersectFull(self):
        for object in self.objects:
            if (object & self.border).any():
                print("BORDER INTERSECT")
        for object1, object2 in itertools.product(self.objects, repeat=2):
            if (object1 & object2).any():
                print("OBJECT INTERSECT")
                