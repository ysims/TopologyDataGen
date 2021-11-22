import math
import numpy as np
import itertools
import scipy.ndimage

# Returns a rotated grid of indices
def rotate_grid(size, rotation, center):
    dimensions = len(center)
    grid = np.indices([size * 2 for _ in range(dimensions)])

    grid[0,0:size*2, 0:size*2, 0:size*2] += center[0] - size
    grid[1,0:size*2, 0:size*2, 0:size*2] += center[1] - size
    grid[2,0:size*2, 0:size*2, 0:size*2] += center[2] - size

    # Scipy uses degrees, so convert rotation from radians to degrees
    degrees_rotation = [x * 180 / math.pi for x in rotation]
    # Get all possible axes to rotate on, and rotate on them
    axes = [x for x in range(dimensions)]
    for axis_1, axis_2 in itertools.combinations(axes, 2):
        current_rotation = degrees_rotation[0]
        degrees_rotation.pop(0)
        for i in range(0, len(grid)):
            grid[i] = scipy.ndimage.rotate(
                grid[i],
                current_rotation,
                axes=(axis_1, axis_2),
                reshape=False,
            )
    # Reverse the padding
    start_slice = [0]
    end_slice = [dimensions]
    for i in range(dimensions):
        start_slice.append(size - center[i])
        end_slice.append((size * 2) - center[i])

    grid = grid[tuple(map(slice, start_slice, end_slice))]

    return grid

# Get the distance in 3d between these two points
def distance3d(point1, point2):
    if (not point1 or not point2) or (len(point1) != 3 or len(point2) != 3):
        return 0
    x_sq = pow((point1[0] - point2[0]), 2)
    y_sq = pow((point1[1] - point2[1]), 2)
    z_sq = pow((point1[2] - point2[2]), 2)
    return np.sqrt(x_sq + y_sq + z_sq)


# Check if a given point intersects or touches something in the grid
def intersect_or_touch(point, grid, object_min_distance):
    # Check if it hits the boundary
    if (max(point) > grid[0][0].size - 1) or min(point) < 0:
        return True

    # Check if this point intersects
    if grid[point[0]][point[1]][point[2]]:
        return True

    # Check if the point touches anything in the grid
    prod = [0]
    for i in range(1, object_min_distance + 1):
        prod.append(i)
        prod.append(-i)
    for x, y, z in itertools.product(prod, repeat=3):
        try:  # skip if this is out of bounds
            if grid[point[0] + x][point[1] + y][
                point[2] + z
            ]:
                return True
        except:
            continue

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

    # Check if the point touches anything in the grid,
    # but ignore if it's on the border
    prod = [0]
    for i in range(object_min_distance):
        prod.append(i)
        prod.append(-i)
    for x, y, z in itertools.product(prod, repeat=3):
        try:  # skip if this is out of bounds
            check_point = [
                point[0] + x,
                point[1] + y,
                point[2] + z,
            ]
            if grid[check_point[0]][check_point[1]][check_point[2]]:
                if (max(check_point) < grid[0][0].size - 1) and min(
                    check_point
                ) > 0:
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