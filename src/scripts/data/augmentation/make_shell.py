import numpy as np
import torch
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

# Convert a grid into a shell
def make_shell(input_file, output_file):
    grid = np.load(input_file)

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
    convolved = convolved.detach().squeeze().squeeze()

    np.save(output_file, convolved.numpy())

    