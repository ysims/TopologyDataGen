import numpy as np
import itertools
import scipy.ndimage
import math


# Returns a rotated grid of indices
def rotate_grid(size, rotation, center):
    dimensions = len(center)
    shape = [size for _ in range(0,dimensions)]
    grid = np.indices(shape)

    # Pad the array so that the desired center is the rotation center
    padX = [grid.shape[1] - center[0], center[0]]
    padY = [grid.shape[2] - center[1], center[1]]
    padZ = [grid.shape[3] - center[2], center[2]]
    grid = np.pad(grid, [[0,0], padX, padY, padZ])

    # Scipy uses degrees, so convert rotation from radians to degrees
    degrees_rotation = [x * 180 / math.pi for x in rotation]

    # Get all possible axes to rotate on, and rotate on them
    axes = [x for x in range(dimensions)]
    for axis_1,axis_2 in itertools.combinations(axes,2):
        current_rotation = degrees_rotation[0]
        degrees_rotation.pop(0)
        for i in range(0, len(grid)):
            grid[i] = scipy.ndimage.rotate(grid[i], current_rotation, axes=(axis_1, axis_2), reshape=False)

    # Reverse the padding
    grid = grid[:, padX[0] : -padX[1], padY[0] : -padY[1], padZ[0] : -padZ[1]]

    return [grid[0], grid[1], grid[2]]


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
