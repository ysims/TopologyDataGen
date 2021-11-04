import os
import yaml
import itertools
import numpy as np
import sys

sys.path.append("../../../datagen")

from BettiCube import BettiCube


def generate_dataset(args):
    path = os.path.join(os.getcwd(), "data/dataset/" + args.save_folder)

    # Create the directory to store the data
    try:
        os.makedirs(path)
    except:
        pass

    count = 0  # for file naming

    # Loop over all configurations of # of object
    # from min to max for all objects
    for i in range(args.min_objects - 1, args.max_objects):
        for _ in range(args.repeat):
            # Set all values to 0, the one we will
            # generate will be changed after
            spheroid_num = 0
            torus_num = 0
            torusN_num = 0
            island_num = 0
            tunnel_num = 0
            octopus_num = 0

            if args.object == "spheroid":
                spheroid_num = i + 1
            elif args.object == "torus":
                torus_num = i + 1
            elif args.object == "torusN":
                torusN_num = i + 1
            elif args.object == "island":
                island_num = i + 1
            elif args.object == "tunnel":
                tunnel_num = i + 1
            elif args.object == "octopus":
                octopus_num = i + 1

            # Create the dictionary to print and use when making objects
            dict = {
                "Spheroid": spheroid_num,
                "Torus": torus_num,
                "TorusN": torusN_num,
                "Island": island_num,
                "Tunnel": tunnel_num,
                "Octopus": octopus_num,
            }
            print("Adding: ", dict)  # print for debugging purposes

            voxels = BettiCube(
                args.cube_size,
                args.shape_config,
                args.random_walk_config,
                args.torus_holes,
            )  # make the cube
            voxels.add_objects(dict)  # add the right number of objects
            grid = voxels.get_objects(draw=True)  # get the objects

            # Create a numpy array from the voxel grid
            numpy_point_cloud = None
            for X, Y, Z in itertools.product(range(0, args.cube_size), repeat=3):
                if grid[X][Y][Z]:
                    if type(numpy_point_cloud) is np.ndarray:
                        numpy_point_cloud = np.concatenate(
                            (numpy_point_cloud, [[X, Y, Z]]), axis=0
                        )
                    else:
                        numpy_point_cloud = np.array([[X, Y, Z]])

            # Write our data
            with open(
                os.path.join(path, "{count}_betti.yaml".format(count=count)), "w"
            ) as file:
                documents = yaml.dump(voxels.get_data(), file)
            np.save(
                os.path.join(path, "{count}_inverted_cube".format(count=count)),
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

            np.save(
                os.path.join(path, "{count}_cube".format(count=count)),
                numpy_point_cloud,
            )

            print("Created data:", count)
            count += 1  # increment our naming counter
