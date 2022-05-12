import itertools
import numpy as np

path = "./data/dataset/4d/tori/S1xS1xB2/1/"
grid = np.load(path + "data.npy")
size = grid.shape[0]

numpy_point_cloud = np.argwhere(grid)

np.save(path + "points.npy", numpy_point_cloud)