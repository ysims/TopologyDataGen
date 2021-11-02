# A script that writes a numpy array of points (ie a point cloud) into a text file
# so that Ripser (original C++ version) can use it

import numpy as np


def ripser_cpp_convert(input_file, output_file):

    # Load the point cloud data
    data = np.load(input_file)

    # Open a text file to write to and
    # loop over all the points in the data and write them to the file
    text_file = open(output_file, "w+")
    for point in data:
        for coord in point:
            text_file.write(str(coord) + " ")
        text_file.write("\n")
    text_file.close()
