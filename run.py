import argparse
import sys

sys.path.append("src/scripts/data/augmentation")
sys.path.append("src/scripts/data/gen")
sys.path.append("src/scripts/data/visualisation")
sys.path.append("src/scripts/persistent_homology")

from invert import invert
from subsample import subsample
from remove_internal import remove_internal
from generate import generate
from run_gudhi import run_gudhi
from ripser_cpp_convert import ripser_cpp_convert
from view_grid import view_grid

parser = argparse.ArgumentParser(description="Helper script to run other scripts")
subparsers = parser.add_subparsers(dest="program", help="sub-command help")

# ***************************
# ***** DATA GENERATION *****
# ***************************
parser_gen = subparsers.add_parser("datagen", help="Generate data.")
parser_gen.add_argument(
    "--cube_size", type=int, default=50, help="Size of the cavity-filled cube, cubed."
)
parser_gen.add_argument(
    "--shape_config",
    default="./Objects/config/Shape.yaml",
    help="The path to the Shape config to use.",
)
parser_gen.add_argument(
    "--random_walk_config",
    default="./Objects/config/RandomWalk.yaml",
    help="The path to the RandomWalk config to use.",
)
parser_gen.add_argument(
    "--torus_holes",
    type=int,
    default=0,
    help="Number of holes in an n-holed torus.",
)
gen_subparsers = parser_gen.add_subparsers(dest="type", help="Generation method")

# Single
single_parser = gen_subparsers.add_parser(
    "single", help="Generate a single data sample."
)
single_parser.add_argument(
    "--spheroid_num",
    type=int,
    default=0,
    help="Number of spheroid cavities to add to the cube.",
)
single_parser.add_argument(
    "--torus_num",
    type=int,
    default=0,
    help="Number of torus cavities to add to the cube.",
)
single_parser.add_argument(
    "--torusN_num",
    type=int,
    default=0,
    help="Number of n-holed torus cavities to add to the cube.",
)
single_parser.add_argument(
    "--island_num",
    type=int,
    default=0,
    help="Number of island cavities to add to the cube.",
)
single_parser.add_argument(
    "--tunnel_num",
    type=int,
    default=0,
    help="Number of tunnel cavities to add to the cube.",
)
single_parser.add_argument(
    "--octopus_num",
    type=int,
    default=0,
    help="Number of octopus cavities to add to the cube.",
)
single_parser.add_argument(
    "--draw", action="store_true", default=False, help="Draws the cube."
)
single_parser.add_argument(
    "--save", action="store_true", default=False, help="Save the data with numpy."
)
single_parser.add_argument(
    "--save_num",
    default="-1",
    help="If saving, number to save the data as.",
)

# Dataset
dataset_parser = gen_subparsers.add_parser("dataset", help="Generate a dataset.")
dataset_parser.add_argument(
    "object",
    choices=["spheroid", "torus", "torusN", "island", "tunnel", "octopus"],
    help="What object type to generate",
)
dataset_parser.add_argument(
    "--min_objects",
    type=int,
    default=1,
    help="The smallest number of objects in any one data point in the dataset",
)
dataset_parser.add_argument(
    "--max_objects",
    type=int,
    default=5,
    help="The highest number of objects in any one data point in the dataset",
)
dataset_parser.add_argument(
    "--repeat",
    type=int,
    default=1000,
    help="Number of times to repeat on one set of parameters.",
)

# ***************************
# **** DATA AUGMENTATION ****
# ***************************
parser_augment = subparsers.add_parser("augment", help="Data augmentation")
parser_augment.add_argument(
    "type",
    choices=["remove_internal", "subsample", "invert", "ripser_cpp_convert"],
    help="Augmentation program to run.",
)
parser_augment.add_argument("input_file", help="Input data file to augment.")
parser_augment.add_argument(
    "output_file", help="File path to save the augmented result to."
)

# ***************************
# *** PERSISTENT HOMOLOGY ***
# ***************************
parser_homology = subparsers.add_parser(
    "homology", help="Run persistent homology software."
)
homology_subparsers = parser_homology.add_subparsers(
    dest="type", help="Generation method"
)

# Gudhi
gudhi_parser = gen_subparsers.add_parser("gudhi", help="Run Gudhi.")
gudhi_parser.add_argument(
    "type",
    choices=["run", "load"],
    help="Whether to run Gudhi on a numpy array or load a pickle file that corresponds to Gudhi output.",
)
gudhi_parser.add_argument(
    "input_file",
    help="The file path of the data to load.",
)
gudhi_parser.add_argument(
    "filtration_type",
    default="vietoris-rips",
    choices=["vietoris-rips", "alpha"],
    help="Type of filtration to use with Gudhi.",
)
gudhi_parser.add_argument(
    "--output_file",
    help="The file path to save the result to.",
)
gudhi_parser.add_argument(
    "--save", action="store_true", default=False, help="Save the data with pickle."
)
gudhi_parser.add_argument(
    "--filtering",
    action="store_true",
    default=False,
    help="Filter the results based on lifetime and print the Betti numbers.",
)
gudhi_parser.add_argument(
    "--vr_threshold",
    type=int,
    help="The threshold value, or max_edge_length, of the Vietoris-Rips complex. Setting this will improve memory usage.",
)
gudhi_parser.add_argument(
    "--b0",
    type=int,
    default=1.0,
    help="The minimum lifetime to use when filtering Betti zero.",
)
gudhi_parser.add_argument(
    "--b1",
    type=int,
    default=1.0,
    help="The minimum lifetime to use when filtering Betti one.",
)
gudhi_parser.add_argument(
    "--b2",
    type=int,
    default=1.0,
    help="The minimum lifetime to use when filtering Betti two.",
)

# ***************************
# ****** VISUALISATION ******
# ***************************
parser_visualise = subparsers.add_parser("visualise", help="Visualise data.")
parser_visualise.add_argument("input_file", help="Data file to view.")

# ***************************
# ******* RUN PROGRAM *******
# ***************************


args = parser.parse_args()

if args.program == "datagen":
    generate(args)
elif args.program == "augment":
    if args.type == "remove_internal":
        remove_internal(args.input_file, args.output_file)
    elif args.type == "subsample":
        subsample(args.input_file, args.output_file)
    elif args.type == "invert":
        invert(args.input_file, args.output_file)
    elif args.type == "ripser_cpp_convert":
        ripser_cpp_convert(args.input_file, args.output_file)
    else:
        sys.exit("Not a valid augmentation program.")
elif args.program == "homology":
    if args.type == "gudhi":
        run_gudhi(args)
elif args.program == "visualise":
    view_grid(args.input_file)
else:
    sys.exit("Unsupported program.")
