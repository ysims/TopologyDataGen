import argparse
import gudhi
import numpy as np
import time
import pickle

# Parse the arguments
parser = argparse.ArgumentParser(
    description="This program loads a voxel grid and runs Ripser on the grid."
)
parser.add_argument(
    "input_number",
    help="The number of the data to load/save.",
)
args = parser.parse_args()

# Load the data
data = np.load(args.input_number + "_cube.npy")
data = data.astype(np.float32)

# Compute the homology
rips_complex = gudhi.RipsComplex(points=data, max_edge_length=3.0)
simplex_tree = rips_complex.create_simplex_tree(max_dimension=3)
diag = simplex_tree.persistence(min_persistence=0.0)

# Save the data
with open(args.input_number + "_output.pickle", "wb") as fp:  # Pickling
    pickle.dump(diag, fp)
