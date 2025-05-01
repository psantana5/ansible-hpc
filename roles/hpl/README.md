# HPL Benchmark Role

This role deploys and runs the High-Performance Linpack (HPL) benchmark on HPC clusters.

## Overview

The High-Performance Linpack (HPL) benchmark is the primary benchmark used to rank supercomputers in the TOP500 list. This role automates the process of:

1. Installing all required dependencies (MPI, BLAS/LAPACK, build tools)
2. Setting up passwordless SSH between compute nodes
3. Downloading, building, and installing HPL from source
4. Generating an optimized HPL.dat configuration file
5. Running the benchmark and collecting results

## Requirements

- Linux-based HPC cluster with multiple compute nodes
- Ansible 2.9 or higher
- Root access on all nodes

## Role Variables

See `defaults/main.yml` for a complete list of variables. Key variables include:

- `mpi_implementation`: MPI implementation to use (openmpi or mpich)
- `blas_implementation`: BLAS/LAPACK implementation (openblas, atlas, etc.)
- `hpl_run_benchmark`: Whether to run the benchmark after setup
- `hpl_mpi_processes`: Number of MPI processes to use
- `hpl_problem_size`: Matrix size (N)
- `hpl_block_size`: Block size (NB)
- `hpl_grid_p` and `hpl_grid_q`: Process grid dimensions

## Usage

```yaml
- hosts: compute
  become: yes
  roles:
    - role: hpl
      tags: [benchmark]