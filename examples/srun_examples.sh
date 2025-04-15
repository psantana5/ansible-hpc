#!/bin/bash

# Basic srun job - runs hostname on a single node
echo "Running basic srun job..."
srun --job-name=basic_srun --time=00:01:00 hostname

# Run a command on multiple tasks
echo "Running multi-task srun job..."
srun --job-name=multi_srun --ntasks=2 --time=00:01:00 hostname

# Run on specific partition
echo "Running job on highmem partition..."
srun --job-name=highmem_srun --partition=highmem --time=00:01:00 free -h

# Run on specific partition with CPU requirements
echo "Running job on highcpu partition..."
srun --job-name=cpu_srun --partition=highcpu --cpus-per-task=4 --time=00:02:00 stress --cpu 4 --timeout 10s

# Interactive job - uncomment to use
# srun --job-name=interactive --pty --time=00:30:00 /bin/bash

# MPI job with srun
echo "Running MPI job with srun..."
srun --job-name=mpi_srun --ntasks=4 --time=00:05:00 mpirun hostname

# Memory-intensive job
echo "Running memory-intensive job..."
srun --job-name=mem_srun --mem=2G --time=00:02:00 bash -c "dd if=/dev/zero of=/tmp/memfile bs=1M count=1024; rm /tmp/memfile"

# Array-like functionality with srun
echo "Running array-like jobs..."
for i in {1..3}; do
  srun --job-name="array_${i}" --time=00:01:00 bash -c "echo Processing task $i; sleep 5"
done