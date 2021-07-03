import numpy as np
import itertools

# General function for creating a homogeneous transformation matrix made up of X-Y-Z rotations
# rotation is a 3d array of x rotation, y rotation, z rotation applied that order.
def get_rotation(rotation):
    X = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, np.cos(rotation[0]), np.sin(rotation[0]), 0.0], [0.0, -np.sin(rotation[0]), np.cos(rotation[0]), 0.0], [0.0, 0.0, 0.0, 1.0]])
    Y = np.array([[np.cos(rotation[1]), 0.0, -np.sin(rotation[1]), 0.0], [0.0, 1.0, 0.0, 0.0], [np.sin(rotation[1]), 0.0, np.cos(rotation[1]), 0.0], [0.0, 0.0, 0.0, 1.0]])
    Z = np.array([[np.cos(rotation[2]), np.sin(rotation[2]), 0.0, 0.0], [-np.sin(rotation[2]), np.cos(rotation[2]), 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
    return Z.dot(Y.dot(X))

# R is a rotation matrix
# C is the center about which we want to rotate - in most cases, the center of the shape we are rotating
# P is a point x,y,z which we are rotating about the center by the angled defined in rotation
def rotate(R, C, P):
    # Homogeneous transformation matrices with the negative center and positive center
    T_neg = np.array([[1.0, 0.0, 0.0, -C[0]], [0.0, 1.0, 0.0, -C[1]], [0.0, 0.0, 1.0, -C[2]], [0.0, 0.0, 0.0, 1.0]])
    T_pos = np.array([[1.0, 0.0, 0.0, C[0]], [0.0, 1.0, 0.0, C[1]], [0.0, 0.0, 1.0, C[2]], [0.0, 0.0, 0.0, 1.0]])
    # Turn the point into a form we can multiply with
    P_full = [P[0], P[1], P[2], 1.0]
    # Return C*R*-C*P - move the origin to the center, rotate the point, then move the origin back
    return T_pos.dot(R.dot(T_neg.dot(P_full)))[:3]

def rotate_grid(size, rotation, center):
    x,y,z = np.indices((size, size, size))
    R = get_rotation(rotation)

    for X,Y,Z in itertools.product(range(0, size), repeat=3):
        x[X][Y][Z],y[X][Y][Z],z[X][Y][Z] = rotate(R, center, [X,Y,Z])

    return x,y,z

# Get the distance in 3d between these two points
def distance3d(point1, point2):
    x_sq = pow((point1[0] - point2[0]), 2)
    y_sq = pow((point1[1] - point2[1]), 2)
    z_sq = pow((point1[2] - point2[2]), 2)
    return np.sqrt(x_sq + y_sq + z_sq)

# Check if a given point intersects or touches something in the grid
def intersect_or_touch(point, grid):
    # Check if this point intersects
    if grid[point[0]][point[1]][point[2]]:
        return True

    # Check if it hits the boundary
    if (max(point) > grid[0][0].size) or min(point) < 0:
        return True
    
    # Check if the point touches anything in the grid
    for x,y,z in itertools.product([-1,0,1],repeat=3):
        try:    # skip if this is out of bounds
            if grid[point[0] + x][point[1] + y][point[2] + z]:
                return True
        except:
            continue
    # Nothing is wrong, so return false
    return False