import numpy as np
import math
import itertools

# General function for creating a homogeneous transformation matrix made up of X-Y-Z rotations
# rotation is a 3d array of x rotation, y rotation, z rotation applied that order.
def getRotation(rotation):
    X = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, np.cos(rotation[0]), np.sin(rotation[0]), 0.0], [0.0, -np.sin(rotation[0]), np.cos(rotation[0]), 0.0], [0.0, 0.0, 0.0, 1.0]])
    Y = np.array([[np.cos(rotation[1]), 0.0, -np.sin(rotation[1]), 0.0], [0.0, 1.0, 0.0, 0.0], [np.sin(rotation[1]), 0.0, np.cos(rotation[1]), 0.0], [0.0, 0.0, 0.0, 1.0]])
    Z = np.array([[np.cos(rotation[2]), np.sin(rotation[2]), 0.0, 0.0], [-np.sin(rotation[2]), np.cos(rotation[2]), 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
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

class Voxels3d:

    def __init__(self, size):
        self.size = size # this should be a 3d array of lengths in the x,y,z directions of our space
        self.objects = [] # initialise our array of objects

    def checkIntersect(self, new_object):
        if len(self.objects) == 0:
            return False
        for object in self.objects:
            new_object = new_object & object
        if new_object.any():
            return True
        return False

    # This will create a wavy circle and add it to the objects
    def addWavyCircle(self, center, radius, rotation):
        x, y, z = np.indices((self.size[0], self.size[1], self.size[2]))
        for X,Y,Z in itertools.product(range(0, 29), repeat=3):
            x[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[0]
            y[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[1]
            z[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[2]
        wavyCircle = (pow(x - center[0], 2) + pow(y - center[1], 2) + pow(z - center[2], 2)) < pow(radius+np.sin(radius*x), 2)
        if self.checkIntersect(wavyCircle):
            print("INTERSECTION")
            return
        self.objects.append(wavyCircle)

    # This will create a circle and add it to the objects
    def addCircle(self, center, radius, rotation):
        x, y, z = np.indices((self.size[0], self.size[1], self.size[2]))
        for X,Y,Z in itertools.product(range(0, 29), repeat=3):
            x[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[0]
            y[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[1]
            z[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[2]
        circle = (pow(x - center[0],2) + pow(y - center[1],2) + pow(z - center[2], 2)) < pow(radius, 2)
        if self.checkIntersect(circle):
            print("INTERSECTION")
            return
        self.objects.append(circle)

    # This will create a torus and add it to the objects
    def addTorus(self, center, major_radius, minor_radius, rotation):
        x, y, z = np.indices((self.size[0], self.size[1], self.size[2]))
        for X,Y,Z in itertools.product(range(0, 29), repeat=3):
            x[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[0]
            y[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[1]
            z[X][Y][Z] = rotate(rotation, center, [X,Y,Z])[2]
        torus = pow((np.sqrt(pow((x - center[0]),2) + pow(y - center[1],2)) - major_radius), 2) + pow(z - center[2], 2) < pow(minor_radius,2)
        if self.checkIntersect(torus):
            print("INTERSECTION")
            return
        self.objects.append(torus)

    def getObjects(self):
        # make a full false grid
        x, y, z = np.indices((self.size[0], self.size[1], self.size[2]))
        first = x + y + z < 0
        for object in self.objects:
            first = first | object
        return first