#!/bin/bash
#PBS -l select=1:ncpus=1:mem=12gb
#PBS -l walltime=200:00:00
#PBS -k oe
#PBS -q allq

echo "Loading Python"

module load python/3.7.3

echo "Moving directory"

cd $PBS_O_WORKDIR

echo "Running dataset"

python generate.py --random_walk_config $VAR1 --shape_config $VAR2 dataset --min_objects $VAR3 --max_objects $VAR3 --repeat 1000 --save_path ./data/grid/$VAR4 --count $VAR5 --object octopus