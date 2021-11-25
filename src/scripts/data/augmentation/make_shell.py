import itertools
import numpy as np
import torch
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

# Convert a grid into a shell
def make_shell(input_file, output_file):
    data = np.load(input_file)
    grid_size = np.amax(data) + 1
    x, y, z = np.indices((grid_size, grid_size, grid_size))
    grid = x == x + 1  # Full falsey grid

    # Loop for each point and set it in the grid
    for point in data:
        grid[point[0]][point[1]][point[2]] = True

    print(grid.shape)
    # Convert the box to a torch tensor
    box_t = torch.from_numpy(grid).float().unsqueeze(0).unsqueeze(0)

    # Create the 3D kernel
    conv = torch.nn.Conv3d(1, 1, 3, stride=1, bias=False, padding=1)

    # c is a + shaped kernel
    c = [
        [[0,0,0],
        [0,1,0],
        [0,0,0]],
                [[0,1,0],
                [1,-1000,1],
                [0,1,0]],
                        [[0,0,0],
                        [0,1,0],
                        [0,0,0]]
        ]
    custom_conv = torch.tensor(c).float()

    # Overwrite the convolution kernel weight with the custom kernel
    conv.weight = torch.nn.Parameter(custom_conv.unsqueeze(0).unsqueeze(0))
    convolved = conv(box_t)     # Convolve the box
    convolved = torch.clamp(convolved, min=0, max=1) 
    
    # Need to collapse the additional dimensions from the 3D convolution (batch and channel dimensions)
    convolved_clone = convolved.detach().squeeze().squeeze()

    # Create the numpy array for the shell
    numpy_point_cloud = None
    for X, Y, Z in itertools.product(range(0, grid_size), repeat=3):
        if convolved_clone[X][Y][Z]:
            if type(numpy_point_cloud) is np.ndarray:
                numpy_point_cloud = np.concatenate(
                    (numpy_point_cloud, [[X, Y, Z]]), axis=0
                )
            else:
                numpy_point_cloud = np.array([[X, Y, Z]])

    np.save(output_file, numpy_point_cloud)

    