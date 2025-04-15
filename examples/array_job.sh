#!/bin/bash
#SBATCH --job-name=array_test
#SBATCH --output=array_test_%A_%a.out
#SBATCH --error=array_test_%A_%a.err
#SBATCH --time=00:05:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=100M
#SBATCH --array=1-5

echo "Array job task $SLURM_ARRAY_TASK_ID started at $(date)"
echo "Running on host: $(hostname)"

# Do something with the array index
echo "Processing data file $SLURM_ARRAY_TASK_ID"
sleep $(( SLURM_ARRAY_TASK_ID * 10 ))

echo "Array job task $SLURM_ARRAY_TASK_ID completed at $(date)"