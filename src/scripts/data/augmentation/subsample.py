# Loads a grid and subsamples the data such that half of the points are removed
# with no two points directly adjacent, ignoring diagonals.
# Intended to be used to increase the performance of persistent homology software
# by creating many small holes that can be easily filtered as noise.

import copy
import itertools
import numpy as np


def subsample(input_file, output_file):
    # Load the data
    original_data = np.load(input_file)
    data = copy.copy(original_data)
    max = np.max(data)
    data = data.tolist()  # list is easier

    # Remove non adjacent points
    print("Subsampling the data.")
    for X, Y, Z in itertools.product(range(0, max + 1), repeat=3):
        if (Z % 2) == 0:
            if ((X + Y) % 2) == 0:
                if [X, Y, Z] in data:
                    data.remove([X, Y, Z])
        else:
            if ((X + Y) % 2) == 1:
                if [X, Y, Z] in data:
                    data.remove([X, Y, Z])

    print(
        "Removed {}/{} points.".format(
            len(original_data) - len(data), len(original_data)
        )
    )

    # Save the result
    data = np.array(data)
    np.save(output_file, data)
