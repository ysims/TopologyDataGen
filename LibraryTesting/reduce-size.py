# Try to reduce the size of the grid, basically random sampling of the grid and remove
import argparse
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
parser.add_argument(
    "remove_perc",
    type=int,
    help="The percentage of the points to remove.",
)
args = parser.parse_args()

data = np.load(args.input_file)
data = data.tolist()  # list is easier

# Get the number of points to remove given the percentage the user wants to remove
num_to_remove = int(len(data) * (args.remove_perc / 100))

np.random.shuffle(data)

# Loop for the number of times to remove an item
for _ in range(num_to_remove):
    data.pop(0)

data = np.array(data)

np.save(args.output_file, data)
