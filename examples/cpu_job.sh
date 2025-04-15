#!/bin/bash
#SBATCH --job-name=cpu_test
#SBATCH --output=cpu_test_%j.out
#SBATCH --error=cpu_test_%j.err
#SBATCH --time=00:15:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=1G
#SBATCH --partition=highcpu

echo "CPU-intensive job started at $(date)"
echo "Running on host: $(hostname)"

# Generate CPU load
echo "Generating CPU load..."
for i in {1..4}; do
  echo "Starting CPU load iteration $i"
  stress --cpu 8 --timeout 30s
  sleep 5
done

echo "CPU-intensive job completed at $(date)"