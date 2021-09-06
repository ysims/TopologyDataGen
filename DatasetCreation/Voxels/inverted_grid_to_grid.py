import argparse
import itertools
import numpy as np

parser = argparse.ArgumentParser(
    description="This program loads a voxel grid and saved the inverted form."
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
parser.add_argument(
    "grid_output",
    help="The file path of the saved grid.",
)
args = parser.parse_args()

np_grid = np.load(args.grid_file)

# Make the normal cube
numpy_point_cloud = None
for X, Y, Z in itertools.product(range(0, args.grid_size), repeat=3):
    if not ([X, Y, Z] in np_grid.tolist()):
        if type(numpy_point_cloud) is np.ndarray:
            numpy_point_cloud = np.concatenate((numpy_point_cloud, [[X, Y, Z]]), axis=0)
        else:
            numpy_point_cloud = np.array([[X, Y, Z]])
# Save the normal cube
np.save(args.grid_output, numpy_point_cloud)
