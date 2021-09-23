#!/bin/bash
#PBS -l select=1:ncpus=1:mem=10gb
#PBS -l walltime=00:05:00
#PBS -k oe
#PBS -q testq

module load python/3.7.3

cd $PBS_O_WORKDIR

# PBS_ARRAY_INDEX is the number from the job array
python run-ripser.py $PBS_ARRAY_INDEX

exit 0