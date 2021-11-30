import itertools
import math
from operator import add
import torch


# Clamps n between smallest and largest possible values
def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


# Get the width of the previous voxel group
def width(previous_points):
    return int(math.log(len(previous_points), 2)) if len(previous_points) > 1 else 1


# Get the border based on direction
def border(direction, width):
    border = []
    prod = [0]
    for i in range(1, width):
        prod.append(i)
    for x, y in itertools.product(prod, repeat=2):
        if x == 0 and y == 0:
            continue
        border.append([x, y])
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


def shell(grid):
    # Convert the box to a torch tensor
    box_t = torch.from_numpy(grid).float().unsqueeze(0).unsqueeze(0)

    # Create the 3D kernel
    conv = torch.nn.Conv3d(1, 1, 3, stride=1, bias=False, padding=1)

    # c is a + shaped kernel
    c = [
        [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
        [[0, 1, 0], [1, -1000, 1], [0, 1, 0]],
        [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
    ]
    custom_conv = torch.tensor(c).float()

    # Overwrite the convolution kernel weight with the custom kernel
    conv.weight = torch.nn.Parameter(custom_conv.unsqueeze(0).unsqueeze(0))
    convolved = conv(box_t)  # Convolve the box
    convolved = torch.clamp(convolved, min=0, max=1)

    # Need to collapse the additional dimensions from the 3D convolution (batch and channel dimensions)
    convolved_clone = convolved.detach().squeeze().squeeze()
    return convolved_clone


def exists_grid(grid, point):
    return grid[point[0]][point[1]][point[2]]


def add_occupancy(grid, point, distance):
    # Add enough points
    prod = [0]
    for i in range(1, distance + 1):
        prod.append(i)
        prod.append(-i)
    for x, y, z in itertools.product(prod, repeat=3):
        try:  # skip if this is out of bounds
            grid[point[0] + x][point[1] + y][point[2] + z] = True
        except:
            continue


def remove_occupancy(grid, point, distance):
    # Remove the points
    prod = [0]
    for i in range(1, distance + 1):
        prod.append(i)
        prod.append(-i)
    for x, y, z in itertools.product(prod, repeat=3):
        try:  # skip if this is out of bounds
            grid[point[0] + x][point[1] + y][point[2] + z] = False
        except:
            continue

def add_occupancy_forward(grid, point, distance, forward):
    prod = [0]
    border = []
    for i in range(1, distance + 1):
        prod.append(i)
        prod.append(-i)
    for x, y in itertools.product(prod, repeat=2):
        border.append([x, y])
    borders = (
        [[0, b[0], b[1]] for b in border]
        if forward[0] != 0
        else [[b[0], 0, b[1]] for b in border]
        if forward[1] != 0
        else [[b[0], b[1], 0] for b in border]
    )
    for border_ in borders:
        try:  # skip if this is out of bounds
            grid_set(grid, add_points(point, border_), True)
        except:
            continue


def grid_set(grid, point, bool):
    grid[point[0]][point[1]][point[2]] = bool


def forward(p1, p2):
    return [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]]


# Given the forward direction of the parent, determine
# what are valid directions for the branch to move initially
def branch_directions(parent_forward):
    return (
        [[0, 1, 0], [0, 0, 1], [0, -1, 0], [0, 0, -1]]
        if parent_forward[0] == 0
        else [
            [1, 0, 0],
            [0, 0, 1],
            [-1, 0, 0],
            [0, 0, -1],
        ]
        if parent_forward[0] == 0
        else [
            [1, 0, 0],
            [0, 1, 0],
            [-1, 0, 0],
            [0, -1, 0],
        ]
    )
