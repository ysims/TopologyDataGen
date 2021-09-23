#!/bin/bash
#PBD -l select=1:ncpus=1:mem=10gb
#PBS -l walltime=00:05:00
#PBS -k oe
#PBS -q testq

module load python/3.7.3

cd $PBS_O_WORKDIR

# VAR1 is the number from the job array
python run-ripser.py $VAR1_cube.npy $VAR1_output.pickle

exit 0