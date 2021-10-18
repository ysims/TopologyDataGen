import argparse
import itertools
import numpy as np

parser = argparse.ArgumentParser(
    description="This program loads a voxel grid and runs Ripser on the grid."
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

# Load the data
data = np.load(args.input_file)
max = np.max(data)
data = data.tolist()  # list is easier
count = 0
count2 = 0
# Remove non adjacent points
for X, Y, Z in itertools.product(range(0, max + 1), repeat=3):
    if (Z % 2) == 0:
        if ((X + Y) % 2) == 0:
            if [X, Y, Z] in data:
                data.remove([X, Y, Z])
                count += 1
            else:
                count2 += 1
    else:
        if ((X + Y) % 2) == 1:
            if [X, Y, Z] in data:
                data.remove([X, Y, Z])
                count += 1
            else:
                count2 += 1

# Save the result
data = np.array(data)
np.save(args.output_file, data)
