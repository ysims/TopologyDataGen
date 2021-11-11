import numpy as np
import itertools
import scipy.ndimage
import math

# Returns a rotated grid of indices
def rotate_grid(size, rotation, center):
    dimensions = len(center)
    grid = np.indices([size * 2 for _ in range(dimensions)])

    for position in itertools.product(range(size * 2), repeat=dimensions):
        for i in range(dimensions):
            grid[i][position[0]][position[1]][position[2]] -= size 
            grid[i][position[0]][position[1]][position[2]] += center[i]

    # Scipy uses degrees, so convert rotation from radians to degrees
    degrees_rotation = [x * 180 / math.pi for x in rotation]

    # Get all possible axes to rotate on, and rotate on them
    axes = [x for x in range(dimensions)]
    for axis_1, axis_2 in itertools.combinations(axes, 2):
        current_rotation = degrees_rotation[0]
        degrees_rotation.pop(0)
        for i in range(0, len(grid)):
            grid[i] = scipy.ndimage.rotate(
                grid[i], current_rotation, axes=(axis_1, axis_2), reshape=False,
            )

    # Reverse the padding
    start_slice = [0]
    end_slice = [dimensions]
    for i in range(dimensions):
        start_slice.append(size - center[i])
        end_slice.append((size * 2) - center[i])

    grid = grid[tuple(map(slice, start_slice, end_slice))]

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
    dimensions = len(point)
    # Get the size of the grid
    grid_size = grid
    for _ in range(dimensions - 1):
        grid_size = grid_size[0]
    grid_size = grid_size.size
    # Check if it hits the boundary
    if (max(point) > grid_size - 1) or min(point) < 0:
        return True

    # Check if this point intersects
    grid_occupancy = grid
    for i in range(dimensions):
        grid_occupancy = grid_occupancy[point[i]]
    if grid_occupancy:
        return True

    # Iteratively check the area around each position which was checked
    # with object_min_distance iterations.
    recurse_points = [point]
    new_recurse_points = []
    for _ in range(object_min_distance):
        for recurse_point in recurse_points:
            # Check if the point touches anything in the grid
            for direction in itertools.product([-1, 0, 1], repeat=dimensions):
                try:  # skip if this is out of bounds
                    new_recurse_points.append(
                        [recurse_point[i] + direction[i] for i in range(dimensions)]
                    )
                    grid_occupancy = grid
                    for i in range(dimensions):
                        grid_occupancy = grid_occupancy[recurse_point[i] + direction[i]]
                    if grid_occupancy:
                        return True
                except:
                    continue
        recurse_points = new_recurse_points
        new_recurse_points = []

    # Nothing is wrong, so return false
    return False


def obj_intersect_touch(point, grid, object_min_distance):
    dimensions = len(point)

    # Get the size of the grid
    grid_size = grid
    for i in range(dimensions - 1):
        grid_size = grid_size[0]
    grid_size = grid_size.size

    # Check if this point intersects,
    # but only if it's not on the border
    try:
        grid_occupancy = grid
        for i in range(dimensions):
            grid_occupancy = grid_occupancy[point[i]]
        if grid_occupancy:
            if (max(point) != grid_size - 1) and min(point) != 0:
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
            for direction in itertools.product([-1, 0, 1], repeat=dimensions):
                try:  # skip if this is out of bounds
                    check_point = [
                        recurse_point[i] + direction[i] for i in range(dimensions)
                    ]
                    new_recurse_points.append(check_point)
                    grid_occupancy = grid
                    for i in range(dimensions):
                        grid_occupancy = grid_occupancy[check_point[i]]
                    if grid_occupancy:
                        if (max(check_point) < grid_size - 1) and min(check_point) > 0:
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
            grid_occupancy = grid
            for i in range(dimensions):
                grid_occupancy = grid_occupancy[point[i] + add[i]]
            if not grid_occupancy:
                return False
        except:
            continue
    # We got through without an empty point - we are surrounded!
    return True


# Check this point is surrounded by the grid or if it's an edge point
# only consider non diagonal points
def hard_surrounded(point, grid):
    dimensions = len(point)

    # Get all possible movement directions
    directions = []
    # Forward directions
    forward_pool = [1]
    for _ in range(0, dimensions - 1):
        forward_pool.append(0)
    for perm in itertools.permutations(forward_pool):
        if directions.count(perm) == 0:
            directions.append(perm)
    # Backward directions
    for perm in itertools.permutations([-x for x in forward_pool]):
        if directions.count(perm) == 0:
            directions.append(perm)

    # Check all the surrounding points and see if they're filled
    for direction in directions:
        try:  # skip if this is out of bounds
            grid_occupancy = grid
            for i in range(dimensions):
                grid_occupancy = grid_occupancy[point[i] + direction[i]]
            if not grid_occupancy:
                return False
        except:
            continue
    # We got through without an empty point - we are surrounded!
    return True
