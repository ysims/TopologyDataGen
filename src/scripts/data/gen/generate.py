from dataset import generate_dataset
from single import create_single_data


def generate(args):
    # Create just one cube with given parameters
    if args.type == "single":
        create_single_data(args)
    # Create a dataset of cubes
    else:
        generate_dataset(args)
