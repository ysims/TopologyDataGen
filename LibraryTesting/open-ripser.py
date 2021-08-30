import pickle
from persim import plot_diagrams

# Open the pickled file
with open("output.txt", "rb") as fp:  # Unpickling
    diagram = pickle.load(fp)

# Plot the persistent homology
plot_diagrams(diagram, show=True)
