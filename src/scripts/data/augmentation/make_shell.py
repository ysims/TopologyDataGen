import numpy as np
import torch
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

# Creating a box with a sphere in it
def make_shell(grid):
    box = np.zeros((62, 62, 62))
    size = grid[0][0].size
    box[3:size+3, 3:size+3, 3:size+3] = grid

    # Convert the box to a torch tensor
    box_t = torch.from_numpy(box).float().unsqueeze(0).unsqueeze(0)

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

    # Need to collapse the additional dimensions from the 3D convolution (batch and channel dimensions)
    convolved_clone = convolved.clone().detach().squeeze().squeeze()
    indices_t = torch.from_numpy(np.indices(convolved_clone.shape))
    

    print(np.array(indices_t))