# This script performs actions to do with running Gudhi on a point cloud dataset.
# run: takes a numpy array of points and runs either the Vietoris-Rips complex or the Alpha complex on it.
#      it may filter the resulting data and print it or save the data in a pickle file.
# load: takes a pickle file with output from Gudhi and filters it and prints it.

import argparse
import gudhi
import numpy as np
import pickle
import sys

# ******************************************************************

# Parse the commands line arguments
parser = argparse.ArgumentParser(
    description="This program loads a voxel grid and runs Gudhi, or loads a pickle file output of Gudhi and filters it."
)
parser.add_argument(
    "type",
    choices=["run", "load"],
    help="Whether to run Gudhi on a numpy array or load a pickle file that corresponds to Gudhi output.",
)
parser.add_argument(
    "input_file",
    help="The file path of the data to load.",
)
parser.add_argument(
    "--output_file",
    help="The file path to save the result to.",
)
parser.add_argument(
    "--save", action="store_true", default=False, help="Save the data with pickle."
)
parser.add_argument(
    "--filtering",
    action="store_true",
    default=False,
    help="Filter the results based on lifetime and print the Betti numbers.",
)
parser.add_argument(
    "filtration_type",
    default="vietoris-rips",
    choices=["vietoris-rips", "alpha"],
    help="Type of filtration to use with Gudhi.",
)
parser.add_argument(
    "--vr_threshold",
    type=int,
    help="The threshold value, or max_edge_length, of the Vietoris-Rips complex. Setting this will improve memory usage.",
)
parser.add_argument(
    "--b0_min_lifetime",
    type=int,
    default=1.0,
    help="The minimum lifetime to use when filtering Betti zero.",
)
parser.add_argument(
    "--b1_min_lifetime",
    type=int,
    default=1.0,
    help="The minimum lifetime to use when filtering Betti one.",
)
parser.add_argument(
    "--b2_min_lifetime",
    type=int,
    default=1.0,
    help="The minimum lifetime to use when filtering Betti two.",
)
args = parser.parse_args()

# ******************************************************************

if args.save and type == "run":
    if args.output_file is None:
        sys.exit("Save option has been chosen but no output file has been specified!")

if type == "run":
    # Load the data
    data = np.load(args.input_file)
    data = data.astype(np.float32)

    # Compute the persistent homology
    if args.filtration_type == "vietoris-rips":
        print("Computing Vietoris-Rips complex.")
        # Run the Vietoris-Rips complex
        # Set the threshold based on user imput if given
        if args.vr_threshold is None:
            rips_complex = gudhi.RipsComplex(points=data)
        else:
            rips_complex = gudhi.RipsComplex(
                points=data, max_edge_length=args.vr_threshold
            )
        simplex_tree = rips_complex.create_simplex_tree(max_dimension=len(data[0]))
        diag = simplex_tree.persistence(min_persistence=0.0)

    elif args.filtration_type == "alpha":
        print("Computing Alpha complex.")
        # Run the Alpha complex
        alpha_complex = gudhi.AlphaComplex(points=data)
        simplex_tree = alpha_complex.create_simplex_tree()
        diag = simplex_tree.persistence(min_persistence=0.0)
    else:
        sys.exit("Unsupported filtration type.")

if type == "load":
    with open(args.input_file, "rb") as fp:
        diag = pickle.load(fp)

# Filter the data
if args.filtering or type == "load":
    b_0, b_1, b_2, b_3 = []

    for entry in diag:
        if entry[0] == 0:
            b_0.append(entry[1])
        elif entry[0] == 1:
            b_1.append(entry[1])
        elif entry[0] == 2:
            b_2.append(entry[1])
        elif entry[0] == 3:
            b_3.append(entry[1])

    b_0 = np.array(b_0).tolist()
    b_1 = np.array(b_1).tolist()
    b_2 = np.array(b_2).tolist()

    b_0 = [life for life in b_0 if (life[1] - life[0] > args.b0_min_lifetime)]
    b_1 = [life for life in b_1 if (life[1] - life[0] > args.b1_min_lifetime)]
    b_2 = [life for life in b_2 if (life[1] - life[0] > args.b2_min_lifetime)]

    print(
        "H0: {}\nH1: {}\nH2: {}\nBetti Numbers: b0={}, b1={}, b2={}".format(
            b_0, b_1, b_2, len(b_0), len(b_1), len(b_2)
        )
    )

if args.save and type == "run":
    # Save the data
    with open(args.output_path, "wb") as fp:  # Pickling
        pickle.dump(diag, fp)
