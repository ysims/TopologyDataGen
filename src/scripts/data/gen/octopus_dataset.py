from subprocess import Popen
from pathlib import Path

octopus_num = 3

commands = []

for stage in range(1, 12):
    path = "octopus/spheroid/{}/".format(stage)
    Path("./data/dataset/" + path).mkdir(parents=True, exist_ok=True)
    random_walk_config = "./src/datagen/config/octopus_gen/RandomWalk{}.yaml".format(
        stage
    )
    shape_config = "./src/datagen/config/octopus_gen/Shape{}.yaml".format(stage)

    commands.append(
        "python run.py datagen --cube_size 50 --random_walk_config {} --shape_config {} dataset octopus --save_folder {}".format(
            random_walk_config, shape_config, path
        )
    )

# run in parallel
processes = [Popen(cmd, shell=True) for cmd in commands]
# wait for completion
for p in processes:
    p.wait()
