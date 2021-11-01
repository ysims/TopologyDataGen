# Loads a grid and subsamples the data such that half of the points are removed
# with no two points directly adjacent, ignoring diagonals.
# Intended to be used to increase the performance of persistent homology software
# by creating many small holes that can be easily filtered as noise.

import argparse
import copy
import itertools
import numpy as np

# ******************************************************************
# Parse the commands line arguments
parser = argparse.ArgumentParser(
    description="This program loads a voxel grid and subsamples half of it."
)
parser.add_argument(
    "input_file",
    help="The file path to the grid to load.",
)
parser.add_argument(
    "output_file",
    help="The file path to save to.",
)
args = parser.parse_args()
# ******************************************************************

# Load the data
original_data = np.load(args.input_file)
data = copy.copy(original_data)
max = np.max(data)
data = data.tolist()  # list is easier

# Remove non adjacent points
print("Subsampling the data.")
for X, Y, Z in itertools.product(range(0, max + 1), repeat=3):
    if (Z % 2) == 0:
        if ((X + Y) % 2) == 0:
            if [X, Y, Z] in data:
                data.remove([X, Y, Z])
    else:
        if ((X + Y) % 2) == 1:
            if [X, Y, Z] in data:
                data.remove([X, Y, Z])

print(
    "Removed {}/{} points.".format(len(original_data) - len(data), len(original_data))
)

# Save the result
data = np.array(data)
np.save(args.output_file, data)
