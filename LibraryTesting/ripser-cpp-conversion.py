import argparse
import numpy as np

parser = argparse.ArgumentParser(
    description="This program loads a numpy point cloud and saves it to a text file."
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


# Open function to open the file "MyFile1.txt"
# (same directory) in append mode and
data = np.load(args.input)

# store its reference in the variable file1
# and "MyFile2.txt" in D:\Text in file2
text_file = open(args.output, "w+")

for point in data:
    for coord in point:
        text_file.write(str(coord) + " ")
    text_file.write("\n")

text_file.close()
