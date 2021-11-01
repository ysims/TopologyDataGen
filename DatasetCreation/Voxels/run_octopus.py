import subprocess
from pathlib import Path

repeats = 20
octopus_num = 3

for experiment in range(1, 12):
    print("Experiment {}.".format(experiment))
    path = "./all_data/single/30-cubed/octopus/spheroid/{}/".format(experiment)
    Path(path).mkdir(parents=True, exist_ok=True)
    random_walk_config = "./Objects/config/octopus_gen/RandomWalk{}.yaml".format(
        experiment
    )
    shape_config = "./Objects/config/octopus_gen/Shape{}.yaml".format(experiment)

    for i in range(0, 20):
        print("Run {}.".format(i))
        sp_path = "./30-cubed/octopus/spheroid/{}/{}".format(experiment, i)
        subprocess.run(
            "python generate.py single --octopus_num {} --cube_size 30 --random_walk_config {} --shape_config {} --save --save_num {}".format(
                octopus_num, random_walk_config, shape_config, sp_path
            )
        )
        print("Subprocess complete. {} / {}".format(experiment, i))
