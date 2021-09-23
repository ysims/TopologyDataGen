import argparse
import gudhi
import matplotlib.pyplot as plt
import numpy as np
import time

parser = argparse.ArgumentParser(
    description="This program loads a voxel grid and runs Ripser on the grid."
)
parser.add_argument(
    "input_file",
    help="The file path to the grid to load.",
)
# parser.add_argument(
#     "output_file",
#     help="The file path to save the result to.",
# )

args = parser.parse_args()

data = np.load(args.input_file)
data = data.astype(np.float32)

# We want to time the computation - start the clock
start = time.perf_counter()
print("Begin!")

rips_complex = gudhi.RipsComplex(points=data, max_edge_length=3.0)

# Finish timing and print the time it took.

simplex_tree = rips_complex.create_simplex_tree(max_dimension=3)

diag = simplex_tree.persistence(min_persistence=0.5)

end = time.perf_counter()
print("Computation took ", (end - start), " seconds")

# print(diag)

b_0 = []
b_1 = []
b_2 = []
b_3 = []

for entry in diag:
    # if entry[1][1] < float("inf"):
    #     continue

    # if entry[1][0] > 1.5:
    #     continue

    if entry[0] == 0:
        b_0.append(entry[1])
    elif entry[0] == 1:
        b_1.append(entry[1])
    elif entry[0] == 2:
        b_2.append(entry[1])
    elif entry[0] == 3:
        b_3.append(entry[1])

print(b_0)
print(b_1)
print(b_2)
# print(b_3)

print("b_0:", len(b_0))
print("b_1:", len(b_1))
print("b_2:", len(b_2))
# print("b_3:", len(b_3))

# # Make it back into the Gudhi form for visualisation
# result = []
# for value in b_0:
#     result.append([0, value])
# for value in b_1:
#     result.append([1, value])
# for value in b_2:
#     result.append([2, value])
# for value in b_3:
#     result.append([3, value])

# gudhi.plot_persistence_barcode(result, legend=True)
# plt.show()

# gudhi.plot_persistence_diagram(result, legend=True)
# plt.show()
