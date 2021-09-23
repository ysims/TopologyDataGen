import argparse
import pickle
from persim import plot_diagrams

parser = argparse.ArgumentParser(
    description="This program loads Ripser output and plots it."
)
parser.add_argument(
    "ripser_file",
    help="The file path to the ripser output to load.",
)

args = parser.parse_args()

# Open the pickled file
with open(args.ripser_file, "rb") as fp:  # Unpickling
    diagram = pickle.load(fp)

# Plot the persistent homology
# plot_diagrams(diagram, show=True)

b_0 = [
    life.tolist() for life in diagram[0] if (life[1] - life[0] > 0.5 and (life[1] > 3))
]
b_1 = [
    life.tolist() for life in diagram[1] if (life[1] - life[0] > 0.2 and life[1] > 1.5)
]
b_2 = [
    life.tolist() for life in diagram[2] if (life[1] - life[0] > 0.8 and life[1] > 3.0)
]
#   [1.4142135381698608, 2.4494898319244385],

print(b_0, b_1, b_2)

print("b_0:", len(b_0))
print("b_1:", len(b_1))
print("b_2:", len(b_2))
