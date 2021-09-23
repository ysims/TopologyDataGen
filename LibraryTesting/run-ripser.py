import argparse
import numpy as np
import os
import pickle
from ripser import ripser
from scipy import sparse
from sklearn.metrics.pairwise import pairwise_distances
import time

path = os.getcwd()


def makeSparseDM(X, thresh):
    N = X.shape[0]
    D = pairwise_distances(X, metric="euclidean")
    [I, J] = np.meshgrid(np.arange(N), np.arange(N))
    I = I[D <= thresh]
    J = J[D <= thresh]
    V = D[D <= thresh]
    return sparse.coo_matrix((V, (I, J)), shape=(N, N)).tocsr()


parser = argparse.ArgumentParser(
    description="This program loads a voxel grid and runs Ripser on the grid."
)
parser.add_argument(
    "input_file",
    help="The file path to the grid to load.",
)
parser.add_argument(
    "output_file",
    help="The file path to the grid to load.",
)

args = parser.parse_args()

data = np.load(args.input_file)
data = data.astype(np.float32)

dim = 2
threshold = 2

start = time.perf_counter()
print("Distance matrix start...")

D = makeSparseDM(data, threshold)

middle = time.perf_counter()
print("Distance matrix computation took ", (middle - start), " seconds.")
print("Now computing persistent homology...")

# Calculate the persistent homology
diagram = ripser(D, maxdim=dim, thresh=threshold, distance_matrix=True)["dgms"]

# Finish timing and print the time it took.
end = time.perf_counter()
print("Ripser computation took ", (end - middle), " seconds")

# Save the diagram by picking
with open(args.output_file, "wb") as fp:  # Pickling
    pickle.dump(diagram, fp)
