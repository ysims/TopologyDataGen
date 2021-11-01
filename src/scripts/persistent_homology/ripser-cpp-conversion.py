# A script that writes a numpy array of points (ie a point cloud) into a text file
# so that Ripser (original C++ version) can use it

import argparse
import numpy as np

# ******************************************************************
# Parse the commands line arguments
parser = argparse.ArgumentParser(
    description="This program loads a numpy point cloud and saves it to a text file for use in Ripser."
)
parser.add_argument(
    "input",
    help="The file path to the numpy point cloud to load.",
)
parser.add_argument(
    "output",
    help="The file path to save the data to.",
)
args = parser.parse_args()
# ******************************************************************

# Load the point cloud data
data = np.load(args.input)

# Open a text file to write to and
# loop over all the points in the data and write them to the file
text_file = open(args.output, "w+")
for point in data:
    for coord in point:
        text_file.write(str(coord) + " ")
    text_file.write("\n")
text_file.close()
