import csv
import gudhi
import math
import numpy as np
import argparse


parser = argparse.ArgumentParser(
    description="This program runs Gudhi for a dataset and puts it into a csv and tex file."
)
parser.add_argument(
    "path",
    help="The path to the data.",
)
parser.add_argument(
    "type",
    choices=["normal", "oct_sph", "oct_torus"],
    help="The type of data",
)
parser.add_argument(
    "file_name",
    help="Name of the csv and tex files.",
)
args = parser.parse_args()

type = args.type
path = args.path
file_name = args.file_name

real_betti_normal = [
    [1, 0, 1],
    [1, 0, 5],
    [1, 0, 10],
    [1, 0, 15],
    [1, 1, 1],
    [1, 2, 2],
    [1, 4, 4],
    [1, 5, 5],
    [1, 2, 1],
    [1, 3, 1],
    [1, 4, 1],
    [1, 5, 1],
    [1, 5, 0],
    [1, 25, 0],
    [1, 35, 0],
    [1, 50, 0],
]
real_betti_octopus_sph = [1, 0, 3]
real_betti_octopus_torus = [1, 3, 3]

repeat = 20

# Prepare the csv file
with open(file_name + ".csv", "w", newline="") as csvfile:
    datawriter = csv.writer(csvfile)
    datawriter.writerow(
        [
            "dataset",
            "v1",
            "v2",
            "v3",
            "v4",
            "v5",
            "v6",
            "v7",
            "v8",
            "v9",
            "v10",
            "v11",
            "v12",
            "v13",
            "v14",
            "v15",
            "v16",
            "v17",
            "v18",
            "v19",
            "v20",
            "a1",
            "a2",
            "a3",
            "a4",
            "a5",
            "a6",
            "a7",
            "a8",
            "a9",
            "a10",
            "a11",
            "a12",
            "a13",
            "a14",
            "a15",
            "a16",
            "a17",
            "a18",
            "a19",
            "a20",
            "vr betti av",
            "alpha betti av",
            "vr betti error",
            "alpha betti error",
            "vr betti std",
            "alpha better std",
        ]
    )

# Prepare the start of the tex file
with open(file_name + ".tex", "w") as f:
    f.write("\\begin{table}[]\n")
    f.write("    \centering\n")
    f.write("    \\begin{tabular}{|c||c|c|c||c|c||c|c|}\n")
    f.write("        \\hline\n")
    f.write(
        "        & \\multicolumn{3}{c||}{Betti ($b_0$,$b_1$,$b_2$)} & \\multicolumn{2}{c||}{Error} & \\multicolumn{2}{c|}{stdev} \\\\ \n"
    )
    f.write("        \\hline \n")
    f.write("         Dataset & True & VR & $\\alpha$ & VR & $\\alpha$ & VR & $\\alpha$ \\\\ \n")
    f.write("        \\hline \n")

# Loop for each data group
num_data = 0
if type == "normal":
    num_data = 16
else:
    # octopus
    num_data = 11

for i in range(1, num_data+1):
    vr_betti = []
    alpha_betti = []

    for j in range(0, repeat):
        print("Progress:", i, "/", j)
        data = np.load(path + str(i) + "/" + str(j) + "_cube.npy")
        data = data.astype(np.float32)

        # GET GUDHI VIETORIS-RIPS RESULT
        rips_complex = gudhi.RipsComplex(points=data, max_edge_length=3.0)
        simplex_rips_tree = rips_complex.create_simplex_tree(max_dimension=3)
        diag_rips = simplex_rips_tree.persistence(min_persistence=0.0)

        print("Completed Vietoris-Rips computation.")

        # FILTER GUDHI VIETORIS-RIPS FEATURES
        b_0 = []
        b_1 = []
        b_2 = []

        for entry in diag_rips:
            if entry[0] == 0:
                b_0.append(entry[1])
            elif entry[0] == 1:
                b_1.append(entry[1])
            elif entry[0] == 2:
                b_2.append(entry[1])

        b_0 = np.array(b_0).tolist()
        b_1 = np.array(b_1).tolist()
        b_2 = np.array(b_2).tolist()

        b_0 = [life for life in b_0 if (life[1] - life[0] > 2.5)]
        b_1 = [life for life in b_1 if (life[1] - life[0] > 0.6)]
        b_2 = [life for life in b_2 if (life[1] - life[0] > 1.5)]

        bettis = [len(b_0), len(b_1), len(b_2)]

        vr_betti.append(bettis)

        print("Filtered Vietoris-Rips.")

        # DO THE SAME THING FOR THE ALPHA COMPLEX
        alpha_complex = gudhi.AlphaComplex(points=data)
        simplex_alpha_tree = alpha_complex.create_simplex_tree()
        diag_alpha = simplex_alpha_tree.persistence(min_persistence=0.0)

        print("Completed Alpha computation.")

        b_0 = []
        b_1 = []
        b_2 = []

        for entry in diag_alpha:
            if entry[0] == 0:
                b_0.append(entry[1])
            elif entry[0] == 1:
                b_1.append(entry[1])
            elif entry[0] == 2:
                b_2.append(entry[1])

        b_0 = np.array(b_0).tolist()
        b_1 = np.array(b_1).tolist()
        b_2 = np.array(b_2).tolist()

        b_0 = [life for life in b_0 if (life[1] - life[0] > 2.5)]
        b_1 = [life for life in b_1 if (life[1] - life[0] > 1.5)]
        b_2 = [life for life in b_2 if (life[1] - life[0] > 2.5)]

        bettis = [len(b_0), len(b_1), len(b_2)]

        alpha_betti.append(bettis)

        print("Filtered Alpha.")

    # Find the mean
    vr_betti_av = [0, 0, 0]
    alpha_betti_av = [0, 0, 0]
    for k in range(0, repeat):
        vr_betti_av[0] += vr_betti[k][0]
        vr_betti_av[1] += vr_betti[k][1]
        vr_betti_av[2] += vr_betti[k][2]
        alpha_betti_av[0] += alpha_betti[k][0]
        alpha_betti_av[1] += alpha_betti[k][1]
        alpha_betti_av[2] += alpha_betti[k][2]

    vr_betti_av = [b / repeat for b in vr_betti_av]
    alpha_betti_av = [b / repeat for b in alpha_betti_av]

    # Find the error
    vr_betti_error = [0, 0, 0]
    alpha_betti_error = [0, 0, 0]

    true = (
        real_betti_normal[i - 1]
        if type == "normal"
        else real_betti_octopus_sph
        if type == "oct_sph"
        else real_betti_octopus_torus
    )
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
        vr_std[0] += (vr_betti[k][0] - vr_betti_av[0]) ** 2
        vr_std[1] += (vr_betti[k][1] - vr_betti_av[1]) ** 2
        vr_std[2] += (vr_betti[k][2] - vr_betti_av[2]) ** 2

        alpha_std[0] += (alpha_betti[k][0] - alpha_betti_av[0]) ** 2
        alpha_std[1] += (alpha_betti[k][1] - alpha_betti_av[1]) ** 2
        alpha_std[2] += (alpha_betti[k][2] - alpha_betti_av[2]) ** 2

    vr_std = [b / repeat for b in vr_std]
    alpha_std = [b / repeat for b in alpha_std]

    vr_std = [math.sqrt(b) for b in vr_std]
    alpha_std = [math.sqrt(b) for b in alpha_std]

    with open(file_name + ".csv", "a", newline="") as csvfile:
        datawriter = csv.writer(csvfile)
        datawriter.writerow(
            [
                i,
                vr_betti[0],
                vr_betti[1],
                vr_betti[2],
                vr_betti[3],
                vr_betti[4],
                vr_betti[5],
                vr_betti[6],
                vr_betti[7],
                vr_betti[8],
                vr_betti[9],
                vr_betti[10],
                vr_betti[11],
                vr_betti[12],
                vr_betti[13],
                vr_betti[14],
                vr_betti[15],
                vr_betti[16],
                vr_betti[17],
                vr_betti[18],
                vr_betti[19],
                alpha_betti[0],
                alpha_betti[1],
                alpha_betti[2],
                alpha_betti[3],
                alpha_betti[4],
                alpha_betti[5],
                alpha_betti[6],
                alpha_betti[7],
                alpha_betti[8],
                alpha_betti[9],
                alpha_betti[10],
                alpha_betti[11],
                alpha_betti[12],
                alpha_betti[13],
                alpha_betti[14],
                alpha_betti[15],
                alpha_betti[16],
                alpha_betti[17],
                alpha_betti[18],
                alpha_betti[19],
                vr_betti_av,
                alpha_betti_av,
                vr_betti_error,
                alpha_betti_error,
                vr_std,
                alpha_std,
            ]
        )

        print("Added a line in accuracy_vr_alpha.csv.")

    with open(file_name + ".tex", "a") as f:
        f.write(
            "        "
            + str(i)
            + " & "
            + str(true)
            + " & "
            + str(vr_betti_av)
            + " & "
            + str(alpha_betti_av)
            + " & "
            + str(vr_betti_error)
            + " & "
            + str(alpha_betti_error)
            + " & "
            + str(vr_std)
            + " & "
            + str(alpha_std)
            + " \\\\\n"
        )
        f.write("\\hline\n")

print("Finished.")
