#!/bin/bash
#SBATCH --job-name=memory_test
#SBATCH --output=memory_test_%j.out
#SBATCH --error=memory_test_%j.err
#SBATCH --time=00:10:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --partition=highmem

echo "Memory-intensive job started at $(date)"
echo "Running on host: $(hostname)"

# Allocate memory
echo "Allocating memory..."
dd if=/dev/zero of=/tmp/memory_file bs=1M count=4000
sleep 30
rm /tmp/memory_file

echo "Memory-intensive job completed at $(date)"