import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D # <--- This is important for 3d plotting 
import itertools
import math

def getRotation(rotation):
    X = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, np.cos(rotation[0]), np.sin(rotation[0]), 0.0], [0.0, -np.sin(rotation[0]), np.cos(rotation[0]), 0.0], [0.0, 0.0, 0.0, 1.0]])
    Y = np.array([[np.cos(rotation[1]), 0.0, -np.sin(rotation[1]), 0.0], [0.0, 1.0, 0.0, 0.0], [np.sin(rotation[1]), 0.0, np.cos(rotation[1]), 0.0], [0.0, 0.0, 0.0, 1.0]])
    Z = np.array([[np.cos(rotation[2]), np.sin(rotation[2]), 0.0, 0.0], [-np.sin(rotation[2]), np.cos(rotation[2]), 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
    return Z.dot(Y.dot(X))

# R is a rotation vector of x,y,z axis rotation (3x3)
# C is the center of the shape
# P is a point x,y,z
def rotate(R, C, P):
    T_minus = np.array([[1.0, 0.0, 0.0, -C[0]], [0.0, 1.0, 0.0, -C[1]], [0.0, 0.0, 1.0, -C[2]], [0.0, 0.0, 0.0, 1.0]])
    T_plus = np.array([[1.0, 0.0, 0.0, C[0]], [0.0, 1.0, 0.0, C[1]], [0.0, 0.0, 1.0, C[2]], [0.0, 0.0, 0.0, 1.0]])
    P_full = [P[0], P[1], P[2], 1.0]
    F = T_plus.dot(R.dot(T_minus.dot(P_full)))
    return F

def getWavyOval(center, radius):
    x, y, z = np.indices((30, 30, 30))
    circle = (pow(x - center,2) + pow(y - center,2) + pow(z - center, 2)) < pow(radius+np.sin(radius*x), 2)
    return circle

def getCircle(center, radius):
    x, y, z = np.indices((30, 30, 30))
    circle = (pow(x - center,2) + pow(y - center,2) + pow(z - center, 2)) < pow(radius, 2)
    return circle

def getTorus(center, major_radius, minor_radius, rotation):
    x,y,z = np.indices((30, 30, 30))
    R = getRotation(rotation)
    for X,Y,Z in itertools.product(range(0, 29), repeat=3):
        x[X][Y][Z] = rotate(R, center, [X,Y,Z])[0]
        y[X][Y][Z] = rotate(R, center, [X,Y,Z])[1]
        z[X][Y][Z] = rotate(R, center, [X,Y,Z])[2]

    torus = pow((np.sqrt(pow((x - center[0]),2) + pow(y - center[1],2)) - major_radius), 2) + pow(z - center[2], 2) < pow(minor_radius,2)
    return torus

# prepare some coordinates
x, y, z = np.indices((30, 30, 30))


# draw cuboids in the top left and bottom right corners, and a link between
# them
circle = getCircle(15, 8)
torus = getTorus([15,15,15], 8, 4, [math.pi/4,-math.pi/4,0])

# combine the objects into a single boolean array
voxels = torus

# set the colors of each object
colors = np.empty(voxels.shape, dtype=object)
colors[circle] = 'blue'

# and plot everything
ax = plt.figure().add_subplot(projection='3d')
ax.voxels(voxels, edgecolor='k')

plt.show()