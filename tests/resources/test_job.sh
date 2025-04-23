#!/bin/bash
#SBATCH --job-name=test_job
#SBATCH --output=/tmp/test_job_%j.out
#SBATCH --error=/tmp/test_job_%j.err
#SBATCH --time=00:05:00
#SBATCH --ntasks=1

# This is a test job script for validating SLURM functionality
hostname
sleep 10
echo "Test job completed successfully"
echo "Environment:"
env
echo "CPU Info:"
lscpu
echo "Memory Info:"
free -h