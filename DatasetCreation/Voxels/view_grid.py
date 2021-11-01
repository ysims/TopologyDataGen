# Loads numpy array (grid) and plots it as a voxel grid with Matplotlib

import argparse
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # <--- This is important for 3d plotting
import numpy as np

# ******************************************************************
# Parse the commands line arguments
parser = argparse.ArgumentParser(
    description="This program loads a voxel grid and plots the grid in matplotlib."
)
parser.add_argument(
    "grid_file",
    help="The file path to the grid to load.",
)
args = parser.parse_args()
# ******************************************************************

# Load array and create a voxel grid from it
np_grid = np.load(args.grid_file)
grid_size = np.amax(np_grid) + 1
x, y, z = np.indices((grid_size, grid_size, grid_size))
grid = x == x + 1  # Full falsey grid

# Loop for each point and set it in the grid
for point in np_grid:
    grid[point[0]][point[1]][point[2]] = True

# Plot the voxel grid with matplotlib
ax = plt.figure().add_subplot(projection="3d")
ax.voxels(grid, edgecolor="k")
plt.show()
