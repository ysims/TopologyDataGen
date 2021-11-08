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

        # Process all from h1 to h3
        for i in range(0,3):
            thresh = b0_thresh if i == 0 else b1_thresh if i==1 else b2_thresh

            # Get the first lifetime
            lifetime = str(f.readline())
            lifetime = lifetime[4 : len(lifetime) - 4]
            pair = lifetime.split(",")

            # Loop until there are no more pairs
            while len(pair) == 2:
                # Set to inf if it doesn't have a death time
                if not is_number(pair[1]):
                    pair[1] = math.inf

                # Check if it satisfies the threshold, then add
                if float(pair[1]) - float(pair[0]) > thresh:
                    if i == 0:
                        b0.append([float(pair[0]), float(pair[1])])
                    if i == 1:
                        b1.append([float(pair[0]), float(pair[1])])
                    if i == 2:
                        b2.append([float(pair[0]), float(pair[1])])
                lifetime = str(f.readline())
                lifetime = lifetime[2 : len(lifetime) - 4]
                pair = lifetime[2:].split(",")

    print(
        "H0: {}\nH1: {}\nH2: {}\nBetti Numbers: b0={}, b1={}, b2={}".format(
            b0, b1, b2, len(b0), len(b1), len(b2)
        )
    )
