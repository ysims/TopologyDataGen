import math


# Clamps n between smallest and largest possible values
def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


# Get the width of the previous voxel group
def width(previous_points):
    return int(math.log(len(previous_points), 2)) if len(previous_points) > 1 else 1

# Get the border based on direction
def border(direction):
    border = [[0, 1], [1, 0], [1, 1]]
    return (
        [[0, b[0], b[1]] for b in border]
        if direction[0] != 0
        else [[b[0], 0, b[1]] for b in border]
        if direction[1] != 0
        else [[b[0], b[1], 0] for b in border]
    )

# Add points piecewise
def add_points(p1, p2):
    return [p1[0] + p2[0], p1[1] + p2[1], p1[2] + p2[2]]
