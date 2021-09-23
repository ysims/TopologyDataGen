import argparse
import numpy as np
import os
import pickle
from ripser import ripser
import time

path = os.getcwd()

parser = argparse.ArgumentParser(
    description="This program loads a voxel grid and runs Ripser on the grid."
)
parser.add_argument(
    "input_file",
    help="The file path to the grid to load.",
)

args = parser.parse_args()

data = np.load(args.input_file + "_cube.npy")

# We want to time the computation - start the clock
start = time.perf_counter()
print("Begin!")

# Calculate the persistent homology
diagram = ripser(data, maxdim=3)["dgms"]

# Finish timing and print the time it took.
end = time.perf_counter()
print("Computation took ", (end - start), " seconds")

# Save the diagram by picking
with open(os.path.join(path, args.input_file), "wb") as fp:  # Pickling
    pickle.dump(diagram, fp)
