import csv
import gudhi
import math
import numpy as np
import argparse
import subprocess
from run_gudhi import run_gudhi
from run_ripser import run_ripser

parser = argparse.ArgumentParser(
    description="This program runs persistent homology software on a dataset and records the results in a csv file."
)
parser.add_argument(
    "path",
    help="The path to the data.",
)
parser.add_argument(
    "file_name",
    help="Name of the csv file.",
)
args = parser.parse_args()

path = args.path
file_name = args.file_name

num_complexities = 7
min_objects = 1
max_objects = 5
repeat = 1000

# Prepare the csv file
with open(file_name + ".csv", "w", newline="") as csvfile:
    datawriter = csv.writer(csvfile)
    datawriter.writerow(
        [
            "dataset",
            "vr betti av",
            "alpha betti av",
            "vr betti error",
            "alpha betti error",
            "vr betti std",
            "alpha better std",
        ]
    )

for complexity in range(1, num_complexities+1):
    for num_objects in range(min_objects, max_objects+1):
        vr_betti = []
        alpha_betti = []

        for j in range(0, repeat):
            print("Progress:", complexity, "/", num_objects, "/", j)
            
            # Gudhi Alpha complex
            gudhi_alpha_args = {
                "type": "run",
                "input_file": "{}/{}/{}_cube.npy".format(path, complexity, str(num_objects * repeat + j)),
                "filtration_type": "alpha",
                "filtering": True,
                "save": False,
                "b0": 1.5,
                "b1": 0.8,
                "b2": 1.5,
            }
            gudhi_results = run_gudhi(gudhi_alpha_args)
            alpha_betti.append([len(x) for x in gudhi_results])

            # Ripser VR complex
            ripser_args = {
                "type": "run",
                "input_file": "{}/{}/{}_cube.npy".format(path, complexity, str(num_objects * repeat + j)),
                "b0": 1.5,
                "b1": 0.8,
                "b2": 1.5,
            }
            ripser_results = run_ripser(ripser_args)
            vr_betti.append([len(x) for x in ripser_results])

        # Find the mean
        vr_betti_av = [0, 0, 0]
        alpha_betti_av = [0, 0, 0]
        for k in range(0, repeat):
            for index in range(0,3):
                vr_betti_av[index] += vr_betti[k][index]
                alpha_betti_av[index] += alpha_betti[k][index]
        vr_betti_av = [b / repeat for b in vr_betti_av]
        alpha_betti_av = [b / repeat for b in alpha_betti_av]

        # Find the error
        vr_betti_error = [0, 0, 0]
        alpha_betti_error = [0, 0, 0]
        true = [1, 0, 1*num_objects]
        for k in range(0, 3):
            if true[k] != 0:
                vr_betti_error[k] = (vr_betti_av[k] - true[k]) / true[k]
                alpha_betti_error[k] = (alpha_betti_av[k] - true[k]) / true[k]
            else:
                vr_betti_error[k] = (vr_betti_av[k] - true[k]) / (1 + true[k])
                alpha_betti_error[k] = (alpha_betti_av[k] - true[k]) / (1 + true[k])

        # Find the standard deviation
        vr_std = [0, 0, 0]
        alpha_std = [0, 0, 0]
        for k in range(0, repeat):
            for index in range(0,3):
                vr_std[index] += (vr_betti[k][index] - vr_betti_av[index]) ** 2
                alpha_std[index] += (alpha_betti[k][index] - alpha_betti_av[index]) ** 2
        vr_std = [b / repeat for b in vr_std]
        alpha_std = [b / repeat for b in alpha_std]
        vr_std = [math.sqrt(b) for b in vr_std]
        alpha_std = [math.sqrt(b) for b in alpha_std]

        with open(file_name + ".csv", "a", newline="") as csvfile:
            datawriter = csv.writer(csvfile)
            datawriter.writerow(
                [
                    complexity,
                    vr_betti_av,
                    alpha_betti_av,
                    vr_betti_error,
                    alpha_betti_error,
                    vr_std,
                    alpha_std,
                ]
            )
        print("Added a line in accuracy_vr_alpha.csv.")

print("Finished.")
