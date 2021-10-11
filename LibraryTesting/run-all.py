import csv
import gudhi
import numpy as np

path = "../DatasetCreation/Voxels/all_data/single/"

with open("accuracy_vr_alpha.csv", "w", newline="") as csvfile:
    datawriter = csv.writer(csvfile)

    # Loop for each data group
    for i in range(1, 17):
        # Ignore these ones cause we aint got them
        if i > 9 and i < 13:
            continue
        # We have five files named from 1-5
        vr_betti = [0, 0, 0]
        alpha_betti = [0, 0, 0]

        for j in range(1, 6):
            print("Progress:", i, "/", j)
            data = np.load(path + str(i) + "/" + str(j) + "_cube.npy")
            data = data.astype(np.float32)

            # GET GUDHI VIETORIS-RIPS RESULT
            rips_complex = gudhi.RipsComplex(points=data, max_edge_length=3.0)
            simplex_tree = rips_complex.create_simplex_tree(max_dimension=3)
            diag = simplex_tree.persistence(min_persistence=0.0)

            print("Completed Vietoris-Rips computation.")

            # FILTER GUDHI VIETORIS-RIPS FEATURES
            b_0 = []
            b_1 = []
            b_2 = []
            b_3 = []

            for entry in diag:
                if entry[0] == 0:
                    b_0.append(entry[1])
                elif entry[0] == 1:
                    b_1.append(entry[1])
                elif entry[0] == 2:
                    b_2.append(entry[1])
                elif entry[0] == 3:
                    b_3.append(entry[1])

            b_0 = np.array(b_0).tolist()
            b_1 = np.array(b_1).tolist()
            b_2 = np.array(b_2).tolist()

            b_0 = [life for life in b_0 if (life[1] - life[0] > 1.0)]
            b_1 = [life for life in b_1 if (life[1] - life[0] > 0.5)]
            b_2 = [life for life in b_2 if (life[1] - life[0] > 1.0)]

            vr_betti[0] += len(b_0)
            vr_betti[1] += len(b_1)
            vr_betti[2] += len(b_2)

            print("Filtered Vietoris-Rips.")

            # DO THE SAME THING FOR THE ALPHA COMPLEX
            alpha_complex = gudhi.AlphaComplex(points=data)
            simplex_tree = rips_complex.create_simplex_tree()
            diag = simplex_tree.persistence(min_persistence=0.0)

            print("Completed Alpha computation.")

            b_0 = []
            b_1 = []
            b_2 = []
            b_3 = []

            for entry in diag:
                if entry[0] == 0:
                    b_0.append(entry[1])
                elif entry[0] == 1:
                    b_1.append(entry[1])
                elif entry[0] == 2:
                    b_2.append(entry[1])
                elif entry[0] == 3:
                    b_3.append(entry[1])

            b_0 = np.array(b_0).tolist()
            b_1 = np.array(b_1).tolist()
            b_2 = np.array(b_2).tolist()

            b_0 = [life for life in b_0 if (life[1] - life[0] > 1.0)]
            b_1 = [life for life in b_1 if (life[1] - life[0] > 0.5)]
            b_2 = [life for life in b_2 if (life[1] - life[0] > 1.0)]

            alpha_betti[0] += len(b_0)
            alpha_betti[1] += len(b_1)
            alpha_betti[2] += len(b_2)

            print("Filtered Alpha.")

        # Now divide them
        vr_betti = [b / 5 for b in vr_betti]
        alpha_betti = [b / 5 for b in alpha_betti]

        datawriter.writerow([i, vr_betti, alpha_betti])

        print("Added a line in accuracy_vr_alpha.csv.")

print("Finished.")
