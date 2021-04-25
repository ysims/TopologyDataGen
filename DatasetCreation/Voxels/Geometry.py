import numpy as np
import itertools

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

def rotate_grid(size, rotation, center):
    x,y,z = np.indices((size, size, size))
    for X,Y,Z in itertools.product(range(0, size), repeat=3):
        x[X][Y][Z],y[X][Y][Z],z[X][Y][Z] = rotate(rotation, center, [X,Y,Z])
    return x,y,z