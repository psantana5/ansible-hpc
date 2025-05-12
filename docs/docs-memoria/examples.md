# Examples for SLURM job submission

1. SLURM array jobs
```bash
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
```

2. CPU-intensive job
```bash
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
```

3. Memory intensive job
```bash
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
```

4. MPI job
```bash
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
```

5. SRUN samples
```bash
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
```