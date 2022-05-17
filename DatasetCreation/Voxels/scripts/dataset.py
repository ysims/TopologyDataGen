import os
import yaml
import itertools
import numpy as np
import random

from BettiCube import BettiCube


def generate_dataset(args):
    path = os.path.join(os.getcwd(), args.save_path)

    octopus_shapes = ["Spheroid", "Torus", "Torus2", "Torus3"]

    # Create the directory to store the data
    try:
        os.mkdir(path)
    except:
        pass

    count_ = args.count + args.repeat
    count = args.count  # for file naming

    # Loop over all configurations of # of object
    # from min to max for all objects
    for i in range(args.min_objects - 1, args.max_objects):
        # Want to have args.repeat number of samples for each # objects, but
        # want to have all permutations of shapes for that # objects
        repeat = int(
            args.repeat
            / len(list(itertools.combinations_with_replacement(octopus_shapes, i + 1)))
        )
        skip = 0
        if repeat == 0:
            skip = int(
                len(
                    list(itertools.combinations_with_replacement(octopus_shapes, i + 1))
                )
                / args.repeat
            )

        for combination in itertools.combinations_with_replacement(
            octopus_shapes, i + 1
        ):
            repeat_ = repeat
            if repeat == 0:
                if skip == 0:
                    repeat_ = 1
                if random.randrange(0, skip) == 0:
                    repeat_ = 1

            for _ in range(repeat_):
                # random.seed(count)

                oct_spheroid = combination.count("Spheroid")
                oct_torus = combination.count("Torus")
                oct_torus2 = combination.count("Torus2")
                oct_torus3 = combination.count("Torus3")

                # Create the dictionary to print and use when making objects
                dict = {
                    "Octopus Spheroid": oct_spheroid,
                    "Octopus Torus": oct_torus,
                    "Octopus Torus2": oct_torus2,
                    "Octopus Torus3": oct_torus3,
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

                four_point_cloud = voxels.get_separate_objects()

                # Write our data
                with open(
                    os.path.join(path, "{count}_betti.yaml".format(count=count)), "w"
                ) as file:
                    yaml.dump(voxels.get_octopus_data(), file)
                np.save(
                    os.path.join(path, "{count}_points.npy".format(count=count)),
                    numpy_point_cloud,
                )
                np.save(
                    os.path.join(path, "{count}_4d_points.npy".format(count=count)),
                    four_point_cloud,
                )
                np.save(
                    os.path.join(path, "{count}_grid.npy".format(count=count)),
                    grid,
                )

                print("Created data:", count)
                count += 1  # increment our naming counter
                if count == count_:
                    return
