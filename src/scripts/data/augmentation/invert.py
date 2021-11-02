# Opens a grid and saves the inverted form of it

import itertools
import numpy as np


def invert(grid_file, grid_output):
    # Open the array
    np_grid = np.load(grid_file)
    grid_size = np.amax(np.data) + 1

    # Make the inverted form of the grid
    numpy_point_cloud = None
    for X, Y, Z in itertools.product(range(0, grid_size), repeat=3):
        if not ([X, Y, Z] in np_grid.tolist()):
            if type(numpy_point_cloud) is np.ndarray:
                numpy_point_cloud = np.concatenate(
                    (numpy_point_cloud, [[X, Y, Z]]), axis=0
                )
            else:
                numpy_point_cloud = np.array([[X, Y, Z]])
    # Save the grid
    np.save(grid_output, numpy_point_cloud)
