import argparse
import pickle
import numpy as np


# Parse the arguments
parser = argparse.ArgumentParser(
    description="This program loads a voxel grid and runs Ripser on the grid."
)
parser.add_argument(
    "input_number",
    help="The number of the data to load/save.",
)
args = parser.parse_args()

# Open the pickled file
with open(args.input_number + "_output.pickle", "rb") as fp:  # Unpickling
    diag = pickle.load(fp)

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

b_0 = np.array(b_0).tolist()
b_1 = np.array(b_1).tolist()
b_2 = np.array(b_2).tolist()

b_0 = [life for life in b_0 if (life[1] - life[0] > 1.5)]
b_1 = [life for life in b_1 if (life[1] - life[0] > 0.42)]
b_2 = [life for life in b_2 if (life[1] - life[0] > 0.84)]

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
