import argparse
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # <--- This is important for 3d plotting
import numpy as np

parser = argparse.ArgumentParser(
    description="This program loads a voxel grid and plots the grid in matplotlib."
)
parser.add_argument(
    "grid_file",
    help="The file path to the grid to load.",
)
parser.add_argument(
    "grid_size",
    type=int,
    help="The size of the grid being loaded.",
)

args = parser.parse_args()

np_grid = np.load(args.grid_file)

x, y, z = np.indices((args.grid_size, args.grid_size, args.grid_size))
grid = x < -9999

for point in np_grid:
    grid[point[0]][point[1]][point[2]] = True

ax = plt.figure().add_subplot(projection="3d")
ax.voxels(grid, edgecolor="k")
plt.show()
