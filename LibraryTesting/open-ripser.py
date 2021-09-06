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
plot_diagrams(diagram, show=True)
