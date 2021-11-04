import numpy as np
import itertools
import scipy.ndimage
import math


# Returns a rotated grid of indices
def rotate_grid(size, rotation, center):
    dimensions = len(center)
    grid = np.indices((size, size, size))
    # Scipy uses degrees, so convert rotation from radians to degrees
    rotation = [x * 180 / math.pi for x in rotation]

    # Move the grid so that the center of the rotation is at the origin
    for X, Y, Z in itertools.product(range(0, size), repeat=3):
        grid[0][X][Y][Z] -= center[0]
        grid[1][X][Y][Z] -= center[1]
        grid[2][X][Y][Z] -= center[2]

    grid[0] = scipy.ndimage.rotate(grid[0], 45, axes=(0, 2), reshape=False)
    grid[1] = scipy.ndimage.rotate(grid[1], 45, axes=(0, 2), reshape=False)
    grid[2] = scipy.ndimage.rotate(grid[2], 45, axes=(0, 2), reshape=False)

    # Move the grid back to its original position
    for X, Y, Z in itertools.product(range(0, size), repeat=3):
        grid[0][X][Y][Z] += center[0]
        grid[1][X][Y][Z] += center[1]
        grid[2][X][Y][Z] += center[2]

    return grid


# Get the distance between these two points
def distanceNd(point1, point2):
    if len(point1) != len(point2):
        print("Error: dimensions of the points differ.")
    dimension = len(point1)
    acc_sq = 0
    for i in range(dimension):
        acc_sq += pow((point1[i] - point2[i]), 2)

    return np.sqrt(acc_sq)


# Check if a given point intersects or touches something in the grid
def intersect_or_touch(point, grid, object_min_distance):
    # Check if it hits the boundary
    if (max(point) > grid[0][0].size - 1) or min(point) < 0:
        return True

    # Check if this point intersects
    if grid[point[0]][point[1]][point[2]]:
        return True

    # Iteratively check the area around each position which was checked
    # with object_min_distance iterations.
    recurse_points = [point]
    new_recurse_points = []
    for _ in range(object_min_distance):
        for recurse_point in recurse_points:
            # Check if the point touches anything in the grid
            for x, y, z in itertools.product([-1, 0, 1], repeat=3):
                try:  # skip if this is out of bounds
                    new_recurse_points.append(
                        [
                            recurse_point[0] + x,
                            recurse_point[1] + y,
                            recurse_point[2] + z,
                        ]
                    )
                    if grid[recurse_point[0] + x][recurse_point[1] + y][
                        recurse_point[2] + z
                    ]:
                        return True
                except:
                    continue
            recurse_points = new_recurse_points
            new_recurse_points = []

    # Nothing is wrong, so return false
    return False


def obj_intersect_touch(point, grid, object_min_distance):
    # Check if this point intersects,
    # but only if it's not on the border
    try:
        if grid[point[0]][point[1]][point[2]]:
            if (max(point) != grid[0][0].size - 1) and min(point) != 0:
                return True
    except:
        # In this case the point is outside of the grid
        # So we don't want it
        return True

    # Iteratively check the area around each position which was checked
    # with object_min_distance iterations.
    recurse_points = [point]
    new_recurse_points = []
    for _ in range(object_min_distance):
        for recurse_point in recurse_points:
            # Check if the point touches anything in the grid,
            # but ignore if it's on the border
            for x, y, z in itertools.product([-1, 0, 1], repeat=3):
                try:  # skip if this is out of bounds
                    check_point = [
                        recurse_point[0] + x,
                        recurse_point[1] + y,
                        recurse_point[2] + z,
                    ]
                    new_recurse_points.append(check_point)
                    if grid[check_point[0]][check_point[1]][check_point[2]]:
                        if (max(check_point) < grid[0][0].size - 1) and min(
                            check_point
                        ) > 0:
                            return True
                except:
                    continue
            recurse_points = new_recurse_points
            new_recurse_points = []
    # Nothing is wrong, so return false
    return False


# Check this point is surrounded by the grid or an edge point
def surrounded(point, grid):
    dimensions = len(point)

    # Check all the surrounding points and see if they're filled
    for add in itertools.product([-1, 0, 1], repeat=dimensions):
        try:  # skip if this is out of bounds
            # If it's empty, we're not surrounded
            gridPoint = grid
            for i in add:
                gridPoint = gridPoint[point[i] + add[i]]
            if not gridPoint:
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
