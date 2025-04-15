#!/bin/bash
#SBATCH --job-name=mpi_test
#SBATCH --output=mpi_test_%j.out
#SBATCH --error=mpi_test_%j.err
#SBATCH --time=00:10:00
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=500M

echo "MPI job started at $(date)"
echo "Running on host: $(hostname)"

# Load MPI module if needed
# module load mpi

# Run MPI program
mpirun hostname
mpirun -np 4 /usr/bin/env

echo "MPI job completed at $(date)"