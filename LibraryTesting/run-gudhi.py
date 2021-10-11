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


# DO THE SAME THING FOR THE ALPHA COMPLEX
alpha_complex = gudhi.AlphaComplex(points=data)
simplex_tree = alpha_complex.create_simplex_tree()
diag = simplex_tree.persistence(min_persistence=0.0)

print("Completed Alpha computation.")

b_0 = []
b_1 = []
b_2 = []
b_3 = []

for entry in diag:
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
b_1 = [life for life in b_1 if (life[1] - life[0] > 0.8)]
b_2 = [life for life in b_2 if (life[1] - life[0] > 2.0)]

print(b_0)
print(b_1)
print(b_2)

print("b_0", len(b_0))
print("b_1", len(b_1))
print("b_2", len(b_2))
