import argparse
import numpy as np
import pickle
from ripser import ripser
import time

parser = argparse.ArgumentParser(
    description="This program loads a voxel grid and runs Ripser on the grid."
)
parser.add_argument(
    "input_file",
    help="The file path to the grid to load.",
)
parser.add_argument(
    "output_file",
    help="The file path to save the result to.",
)

args = parser.parse_args()

data = np.load(args.input_file)

# We want to time the computation - start the clock
start = time.perf_counter()
print("Begin!")

# Calculate the persistent homology
diagram = ripser(data, maxdim=3)["dgms"]

# Finish timing and print the time it took.
end = time.perf_counter()
print("Computation took ", (end - start), " seconds")

# Save the diagram by picking
with open(args.output_file, "wb") as fp:  # Pickling
    pickle.dump(diagram, fp)
