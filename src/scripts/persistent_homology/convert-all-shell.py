import sys
sys.path.append("./src/scripts/data/augmentation/")

from make_shell import make_shell

path = "./data/dataset/octopus/spheroid/"

# For each folder in the spheroid octopus dataset
for i in range(1,12):
    folder_path = path + str(i) + "/"
    # For each data in the folder
    for j in range(5):
        input_file = folder_path + str(j) + "_inverted_cube.npy"
        output_file = folder_path + str(j) + "_shell.npy"
        make_shell(input_file, output_file)