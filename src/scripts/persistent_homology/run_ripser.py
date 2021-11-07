import math


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def run_ripser(args):
    b0 = []
    b1 = []
    b2 = []

    b0_thresh = 1.0
    b1_thresh = 1.0
    b2_thresh = 1.0

    with open(args.input_file, "rb") as f:
        f.readline()  # point cloud with x points in dimension y
        f.readline()  # persistence intervals in dim 0:
        lifetime = str(f.readline())
        # Process all b0
        while lifetime != "persistence intervals in dim 1:":
            pair = lifetime[4 : len(lifetime) - 4].split(",")
            print(pair)
            if not is_number(pair[1]):
                pair[1] = math.inf

            if float(pair[1]) - float(pair[0]) > b0_thresh:
                b0.append([float(pair[0]), float(pair[1])])
            lifetime = str(f.readline())
            print(lifetime)

        # now lifetime is "persistence ... dim 1:"
        lifetime = str(f.readline())
        # Process all b1
        while lifetime != "persistence intervals in dim 2:":
            pair = lifetime[4 : len(lifetime) - 4].split(",")
            if pair[1] == " ":
                pair[1] == float("inf")
            if float(pair[1]) - float(pair[0]) > b1_thresh:
                b1.append(float(pair[0]), float(pair[1]))
            lifetime = str(f.readline())

        # now lifetime is "persistence ... dim 2:"
        lifetime = str(f.readline())
        # Process all b2
        while lifetime != "":
            pair = lifetime[4 : len(lifetime) - 4].split(",")
            if pair[1] == " ":
                pair[1] == float("inf")
            if float(pair[1]) - float(pair[0]) > b2_thresh:
                b2.append(float(pair[0]), float(pair[1]))
            lifetime = str(f.readline())

    print(
        "H0: {}\nH1: {}\nH2: {}\nBetti Numbers: b0={}, b1={}, b2={}".format(
            b0, b1, b2, len(b0), len(b1), len(b2)
        )
    )
