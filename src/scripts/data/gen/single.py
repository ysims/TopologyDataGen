import itertools
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # <--- This is important for 3d plotting
import numpy as np
import os
import random
import yaml
import sys

sys.path.append("../../../datagen")
sys.path.append("../augmentation")

from BettiCube import BettiCube
from make_shell import make_shell

# Create a single cube
def create_single_data(args):
    # Create the dictionary to print and use when making objects
    dict = {
        "Spheroid": args.spheroid_num,
        "Torus": args.torus_num,
        "TorusN": args.torusN_num,
        "Island": args.island_num,
        "Tunnel": args.tunnel_num,
        "Octopus": args.octopus_num,
    }

    print("Adding: ", dict)
    start_time = time.time()

    config_path = "./src/datagen/config/"
    # Create the cube with the given holes
    voxels = BettiCube(
        args.cube_size, config_path + args.shape_config, config_path + args.random_walk_config, args.torus_holes
    )
    voxels.add_objects(dict)

    print("Adding --------- %s seconds ---" % (time.time() - start_time))

    # Draw the grid with matplotlib
    if args.draw:
        ax = plt.figure().add_subplot(projection="3d")
        ax.voxels(voxels.get_objects(draw=True), edgecolor="k")
        plt.show()

    # Save the cube with numpy
    if args.save:
        path = os.path.join(os.getcwd(), "data/single")

        # Create the directory to store any data
        try:
            os.makedirs(path)
        except:
            pass

        # Create the numpy array for the inverted cube
        grid = voxels.get_objects(draw=True)
        numpy_point_cloud = None
        for X, Y, Z in itertools.product(range(0, args.cube_size), repeat=3):
            if grid[X][Y][Z]:
                if type(numpy_point_cloud) is np.ndarray:
                    numpy_point_cloud = np.concatenate(
                        (numpy_point_cloud, [[X, Y, Z]]), axis=0
                    )
                else:
                    numpy_point_cloud = np.array([[X, Y, Z]])
        # Save the inverted cube
        if args.save_num == "-1":
            r_num = str(random.randint(0, 99999))
        else:
            r_num = args.save_num
        np.save(
            os.path.join(path, "{r_num}_inverted_cube".format(r_num=r_num)),
            numpy_point_cloud,
        )

        # Make the normal cube
        numpy_point_cloud = None
        for X, Y, Z in itertools.product(range(0, args.cube_size), repeat=3):
            if not grid[X][Y][Z]:
                if type(numpy_point_cloud) is np.ndarray:
                    numpy_point_cloud = np.concatenate(
                        (numpy_point_cloud, [[X, Y, Z]]), axis=0
                    )
                else:
                    numpy_point_cloud = np.array([[X, Y, Z]])
        # Save the normal cube
        np.save(
            os.path.join(path, "{r_num}_cube".format(r_num=r_num)), numpy_point_cloud
        )
        # Save the metadata
        with open(
            os.path.join(path, "{r_num}_betti.yaml".format(r_num=r_num)), "w"
        ) as file:
            documents = yaml.dump(voxels.get_data(), file)

        print("Saved as", r_num)