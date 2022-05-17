#!/bin/bash

# Created by c3256711, last update: 02/09/2021.
#PBS -l select=1:ncpus=1:mem=100MB
#PBS -l walltime=00:05:00
#PBS -k oe

module load python/3.7.3

cd $PBS_O_WORKDIR

# VAR1 is '--spheroid_num' or whatever shape
# VAR2 is the number of that shape
# VAR3 is cube size
python ./generate.py single $VAR1 $VAR2 --cube_size $VAR3 --save

exit 0