from ripser import ripser
import time
import pickle
import numpy as np

data = np.load("point_cloud.npy")

# We want to time the computation - start the clock
start = time.perf_counter()
print("Begin!")

# Calculate the persistent homology
diagram = ripser(data, maxdim=3)["dgms"]

# Finish timing and print the time it took.
end = time.perf_counter()
print("Computation took ", (end - start), " seconds")

# Save the diagram by picking
with open("output.txt", "wb") as fp:  # Pickling
    pickle.dump(diagram, fp)
