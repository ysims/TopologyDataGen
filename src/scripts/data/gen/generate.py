import argparse
import sys

sys.path.append("scripts")

from dataset import generate_dataset
from single import create_single_data

# ***** OPTIONS *****
# Generic
parser = argparse.ArgumentParser(
    description="This program creates and draws cavity-filled cube/s"
)
parser.add_argument(
    "type",
    default="single",
    choices=["single", "dataset"],
    help="Type of generation - a single cube or a whole dataset.",
)
parser.add_argument(
    "--cube_size", type=int, default=50, help="Size of the cavity-filled cube, cubed."
)
parser.add_argument(
    "--shape_config",
    default="./Objects/config/Shape.yaml",
    help="The path to the Shape config to use.",
)
parser.add_argument(
    "--random_walk_config",
    default="./Objects/config/RandomWalk.yaml",
    help="The path to the RandomWalk config to use.",
)

parser.add_argument(
    "--torus_holes",
    type=int,
    default=0,
    help="Number of holes in an n-holed torus.",
)

# Single specific
parser.add_argument(
    "--spheroid_num",
    type=int,
    default=0,
    help="Number of spheroid cavities to add to the cube.",
)
parser.add_argument(
    "--torus_num",
    type=int,
    default=0,
    help="Number of torus cavities to add to the cube.",
)
parser.add_argument(
    "--torusN_num",
    type=int,
    default=0,
    help="Number of n-holed torus cavities to add to the cube.",
)
parser.add_argument(
    "--island_num",
    type=int,
    default=0,
    help="Number of island cavities to add to the cube.",
)
parser.add_argument(
    "--tunnel_num",
    type=int,
    default=0,
    help="Number of tunnel cavities to add to the cube.",
)
parser.add_argument(
    "--octopus_num",
    type=int,
    default=0,
    help="Number of octopus cavities to add to the cube.",
)
parser.add_argument(
    "--draw", action="store_true", default=False, help="Draws the cube."
)
parser.add_argument(
    "--save", action="store_true", default=False, help="Save the data with numpy."
)
parser.add_argument(
    "--save_num",
    default="-1",
    help="If saving, number to save the data as.",
)

# Dataset specific
# TODO: Allow for multiple objects
parser.add_argument(
    "--object",
    choices=["spheroid", "torus", "torusN", "island", "tunnel", "octopus"],
    help="What object type to generate",
)
parser.add_argument(
    "--min_objects",
    type=int,
    default=1,
    help="The smallest number of objects in any one data point in the dataset",
)
parser.add_argument(
    "--max_objects",
    type=int,
    default=5,
    help="The highest number of objects in any one data point in the dataset",
)
parser.add_argument(
    "--repeat",
    type=int,
    default=1000,
    help="Number of times to repeat on one set of parameters.",
)

args = parser.parse_args()

# **** MAKE THE DATA ****
# Create just one cube with given parameters
if args.type == "single":
    create_single_data(args)

# Create a dataset of cubes
else:
    if args.object is None:
        parser.error("Dataset mode requires --object")
    generate_dataset(args)
