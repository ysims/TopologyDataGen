import argparse
import sys

sys.path.append("src/scripts/data/augmentation")
sys.path.append("src/scripts/data/gen")
sys.path.append("src/scripts/data/visualisation")
sys.path.append("src/scripts/persistent_homology")

from invert import invert
from subsample import subsample
from remove_internal import remove_internal

parser = argparse.ArgumentParser(description="Helper script to run other scripts")
subparsers = parser.add_subparsers(dest="program", help="sub-command help")

# ***************************
# ***** DATA GENERATION *****
# ***************************
parser_gen = subparsers.add_parser("datagen", help="Generate data.")
parser_gen.add_argument("--number", type=int, help="type a number")

# ***************************
# **** DATA AUGMENTATION ****
# ***************************
parser_augment = subparsers.add_parser("augment", help="Data augmentation")
parser_augment.add_argument(
    "type",
    choices=["remove_internal", "subsample", "invert"],
    help="Augmentation program to run.",
)
parser_augment.add_argument("input_file", help="Input data file to augment.")
parser_augment.add_argument(
    "output_file", help="File path to save the augmented result to."
)


args = parser.parse_args()

if args.program == "augment":
    if args.type == "remove_internal":
        invert(args.input_file, args.output_file)
    elif args.type == "subsample":
        subsample(args.input_file, args.output_file)
    elif args.type == "invert":
        invert(args.input_file, args.output_file)
    else:
        sys.exit("Not a valid augmentation program.")
