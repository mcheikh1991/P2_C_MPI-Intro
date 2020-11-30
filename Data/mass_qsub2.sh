#!/bin/bash
#$ -l mem=1.5G
#$ -l h_rt=24:00:00
#$ -l killable
#$ -cwd
#$ -q \*@@elves
#$ -pe mpi-spread 2
mpirun -np 2 /homes/mcheikh/CIS_625/hw3/MPI_V2.out 1000000 12644
hostname
echo -e "---Done---\n"8
mpirun -np 2 /homes/mcheikh/CIS_625/hw3/MPI_V2.out 800000 12644
hostname
echo -e "---Done---\n"
mpirun -np 2 /homes/mcheikh/CIS_625/hw3/MPI_V2.out 600000 12644
hostname
echo -e "---Done---\n"
mpirun -np 2 /homes/mcheikh/CIS_625/hw3/MPI_V2.out 400000 12644
hostname
echo -e "---Done---\n"
mpirun -np 2 /homes/mcheikh/CIS_625/hw3/MPI_V2.out 200000 12644
hostname
echo -e "---Done---\n"

