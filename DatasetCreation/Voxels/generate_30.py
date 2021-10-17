import subprocess
from pathlib import Path

repeats = 20
number_of = [
    "--spheroid_num 1",
    "--spheroid_num 5",
    "--spheroid_num 10",
    "--spheroid_num 15",
    "--torus_num 1",
    "--torus_num 2",
    "--torus_num 4",
    "--torus_num 5",
    "--torusN_num 1 --torus_holes 2",
    "--torusN_num 1 --torus_holes 3",
    "--torusN_num 1 --torus_holes 4",
    "--torusN_num 1 --torus_holes 5",
    "--tunnel_num 5",
    "--tunnel_num 25",
    "--tunnel_num 35",
    "--tunnel_num 50",
]

for experiment in range(0, len(number_of)):
    print("Experiment {}.".format(experiment))
    path = "./all_data/single/30-cubed/normal/{}/".format(experiment + 1)
    Path(path).mkdir(parents=True, exist_ok=True)
    for i in range(0, 20):
        print("Run {}.".format(i))
        sp_path = "./30-cubed/normal/{}/{}".format(experiment, i)
        subprocess.run(
            "python generate.py single {} --cube_size 30 --save --save_num {}".format(
                number_of[experiment], sp_path
            )
        )
        print("Subprocess complete. {} / {}".format(experiment, i))
