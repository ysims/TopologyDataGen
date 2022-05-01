from subprocess import Popen
from pathlib import Path

commands = []

for stage in range(1, 10):
    path = "all_data/16-04-2022/{}/".format(stage)
    Path(path).mkdir(parents=True, exist_ok=True)
    random_walk_config = "./Objects/config/config/RandomWalk{}.yaml".format(
        stage
    )
    shape_config = "./Objects/config/config/Shape{}.yaml".format(stage)

    commands.append(
        "python generate.py dataset --cube_size 64 --random_walk_config {} --shape_config {} --object octopus --save_path {} --repeat 2000 --min_objects 25 --max_objects 50".format(
            random_walk_config, shape_config, path
        )
    )

# run in parallel
processes = [Popen(cmd, shell=True) for cmd in commands]
# wait for completion
for p in processes:
    p.wait()