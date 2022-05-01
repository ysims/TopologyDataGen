import numpy as np
import itertools
import time

# General function for creating a homogeneous transformation matrix
# made up of X-Y-Z rotations
# rotation is a 3d array of x rotation,
# y rotation, z rotation applied that order.
def get_rotation(rotation):
    X = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, np.cos(rotation[0]), np.sin(rotation[0]), 0.0],
            [0.0, -np.sin(rotation[0]), np.cos(rotation[0]), 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    Y = np.array(
        [
            [np.cos(rotation[1]), 0.0, -np.sin(rotation[1]), 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [np.sin(rotation[1]), 0.0, np.cos(rotation[1]), 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    Z = np.array(
        [
            [np.cos(rotation[2]), np.sin(rotation[2]), 0.0, 0.0],
            [-np.sin(rotation[2]), np.cos(rotation[2]), 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    return Z.dot(Y.dot(X))


# R is a rotation matrix
# C is the center about which we want to rotate - in most cases,
#   the center of the shape we are rotating
# P is a point x,y,z which we are rotating about the center
#   by the angled defined in rotation
def rotate(R, C, P):
    # Homogeneous transformation matrices with the
    # negative center and positive center
    T_neg = np.array(
        [
            [1.0, 0.0, 0.0, -C[0]],
            [0.0, 1.0, 0.0, -C[1]],
            [0.0, 0.0, 1.0, -C[2]],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    T_pos = np.array(
        [
            [1.0, 0.0, 0.0, C[0]],
            [0.0, 1.0, 0.0, C[1]],
            [0.0, 0.0, 1.0, C[2]],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    # Turn the point into a form we can multiply with
    P_full = [P[0], P[1], P[2], 1.0]
    # Return C*R*(-C)*P - move the origin to the center,
    # rotate the point, then move the origin back
    return T_pos.dot(R.dot(T_neg.dot(P_full)))[:3]


# Returns a rotated grid of indices
def rotate_grid(size, rotation, center):
    x, y, z = np.indices((size, size, size))
    R = get_rotation(rotation)

    for X, Y, Z in itertools.product(range(0, size), repeat=3):
        x[X][Y][Z], y[X][Y][Z], z[X][Y][Z] = rotate(R, center, [X, Y, Z])

    return x, y, z


# Get the distance in 3d between these two points
def distance3d(point1, point2):
    if (not point1 or not point2) or (len(point1) != 3 or len(point2) != 3):
        return 0
    x_sq = pow((point1[0] - point2[0]), 2)
    y_sq = pow((point1[1] - point2[1]), 2)
    z_sq = pow((point1[2] - point2[2]), 2)
    return np.sqrt(x_sq + y_sq + z_sq)


# Check if a given point intersects or touches something in the grid
def intersect_or_touch(point, grid):
    # Check if it hits the boundary
    if (max(point) > grid[0][0].size - 1) or min(point) < 0:
        return True

    # Check if this point intersects
    if grid[point[0]][point[1]][point[2]]:
        return True

    # Check if the point touches anything in the grid
    for x, y, z in itertools.product([-1, 0, 1], repeat=3):
        try:  # skip if this is out of bounds
            if grid[point[0] + x][point[1] + y][point[2] + z]:
                return True
        except:
            continue
    # Nothing is wrong, so return false
    return False

def forward(p1, p2):
    return [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]]

def obj_intersect_touch(point, grid):
    # Check if this point intersects,
    # but only if it's not on the border
    if grid[point[0]][point[1]][point[2]]:
        if (max(point) != grid[0][0].size - 1) and min(point) != 0:
            return True

    # Check if the point touches anything in the grid,
    # but ignore if it's on the border
    for x, y, z in itertools.product([-1, 0, 1], repeat=3):
        try:  # skip if this is out of bounds
            touch_point = [point[0] + x, point[1] + y, point[2] + z]
            if grid[touch_point[0]][touch_point[1]][touch_point[2]]:
                if (max(touch_point) < grid[0][0].size - 1) and min(touch_point) > 0:
                    return True
        except:
            continue
    # Nothing is wrong, so return false
    return False


# Check this point is surrounded by the grid or an edge point
def surrounded(point, grid):
    # Check all the surrounding points and see if they're filled
    for x, y, z in itertools.product([-1, 0, 1], repeat=3):
        try:  # skip if this is out of bounds
            # If it's empty, we're not surrounded
            if not grid[point[0] + x][point[1] + y][point[2] + z]:
                return False
        except:
            continue
    # We got through without an empty point - we are surrounded!
    return True


# Check this point is surrounded by the grid or if it's an edge point
# only consider non diagonal points
def hard_surrounded(point, grid):
    directions = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [-1, 0, 0], [0, -1, 0], [0, 0, -1]]
    # Check all the surrounding points and see if they're filled
    for direction in directions:
        try:  # skip if this is out of bounds
            if not (
                grid[point[0] + direction[0]][point[1] + direction[1]][
                    point[2] + direction[2]
                ]
            ):
                return False
        except:
            continue
    # We got through without an empty point - we are surrounded!
    return True


# Rotate just the object, not the whole grid
def rotate_object(object, grid):
    R = get_rotation(object.rotation)  # get the rotation matrix

    # Loop for all indices but only do something
    # if it's a voxel in the object
    for X, Y, Z in itertools.product(range(0, grid[0][0].size), repeat=3):
        if grid[X][Y][Z]:
            x, y, z = rotate(R, object.center, [X, Y, Z])
            try:
                # Make the new position true (moving the voxel to here)
                grid[int(round(x))][int(round(y))][int(round(z))] = True
            except:
                # The point could rotate out of the grid.
                # This'll be flagged as intersecting with the
                # boundary anyway, but we could handle this in the
                # future by returning a bool or something
                # that might quicken things up by stopping early
                # if it's obviously not gonna work
                pass
            # The old position is now false (voxel has gone)
            grid[X][Y][Z] = False
