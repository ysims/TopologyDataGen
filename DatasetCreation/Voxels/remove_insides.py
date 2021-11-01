import argparse
import itertools
import numpy as np

import sys

sys.path.append("Objects")
from Geometry import surrounded

# Parse arguments
parser = argparse.ArgumentParser(
    description="This program loads a voxel grid and saves it without its insides."
)
parser.add_argument(
    "grid_file",
    help="The file path to the grid to load.",
)
parser.add_argument(
    "grid_output",
    help="The file path of the saved grid.",
)
args = parser.parse_args()

data = np.load(args.grid_file)
new_grid = []

grid_size = np.amax(data) + 1
x, y, z = np.indices((grid_size, grid_size, grid_size))
data_grid = x == x + 1  # Full falsey grid

# Loop for each point and set it in the grid
for point in data:
    data_grid[point[0]][point[1]][point[2]] = True

for point in data:
    if not surrounded(point, data_grid):
        new_grid.append(point)

np.save(args.grid_output, new_grid)
