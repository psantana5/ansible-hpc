#!/bin/bash
# Manual power data collection script for Slurm nodes
# This script collects power data and writes it directly to Prometheus textfile collector

METRICS_FILE="/var/lib/node_exporter/textfile_collector/power_metrics.prom"
HOSTNAME=$(hostname)
COLLECTION_INTERVAL=30  # 30 seconds between collections

# Function to estimate CPU power based on load
estimate_cpu_power() {
    # Get CPU load
    load=$(cat /proc/loadavg | awk '{print $1}')
    
    # Get number of CPUs
    cpu_count=$(nproc)
    
    # Calculate load percentage (capped at 100%)
    load_percent=$(echo "scale=2; min(100, ($load / $cpu_count) * 100)" | bc)
    
    # Estimate power: base power + additional power based on load
    base_power=10  # Watts at idle
    max_additional_power=90  # Additional watts at 100% load
    
    estimated_power=$(echo "scale=2; $base_power + ($max_additional_power * $load_percent / 100)" | bc)
    echo $estimated_power
}

# Function to estimate memory power consumption
estimate_memory_power() {
    # Get memory info
    total_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    available_kb=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
    
    # Calculate used memory and usage percentage
    used_kb=$((total_kb - available_kb))
    usage_percent=$(echo "scale=2; ($used_kb / $total_kb) * 100" | bc)
    
    # Estimate power: base power + additional power based on usage
    base_power=5  # Watts at idle
    max_additional_power=15  # Additional watts at 100% usage
    
    estimated_power=$(echo "scale=2; $base_power + ($max_additional_power * $usage_percent / 100)" | bc)
    echo $estimated_power
}

# Function to get GPU power if available
get_gpu_power() {
    if command -v nvidia-smi &> /dev/null; then
        power=$(nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits | awk '{sum += $1} END {print sum}')
        if [ -z "$power" ]; then
            echo "0"
        else
            echo $power
        fi
    else
        echo "0"
    fi
}

# Function to collect and write metrics
collect_and_write_metrics() {
    # Get power data
    cpu_power=$(estimate_cpu_power)
    memory_power=$(estimate_memory_power)
    gpu_power=$(get_gpu_power)
    
    # Calculate total power
    total_power=$(echo "$cpu_power + $memory_power + $gpu_power" | bc)
    
    # Create metrics file
    echo "# HELP node_power_usage_watts Current power usage in watts" > $METRICS_FILE
    echo "# TYPE node_power_usage_watts gauge" >> $METRICS_FILE
    echo "node_power_usage_watts{hostname=\"$HOSTNAME\"} $total_power" >> $METRICS_FILE
    
    echo "# HELP node_cpu_power_watts CPU power usage in watts" >> $METRICS_FILE
    echo "# TYPE node_cpu_power_watts gauge" >> $METRICS_FILE
    echo "node_cpu_power_watts{hostname=\"$HOSTNAME\"} $cpu_power" >> $METRICS_FILE
    
    echo "# HELP node_memory_power_watts Memory power usage in watts" >> $METRICS_FILE
    echo "# TYPE node_memory_power_watts gauge" >> $METRICS_FILE
    echo "node_memory_power_watts{hostname=\"$HOSTNAME\"} $memory_power" >> $METRICS_FILE
    
    echo "# HELP node_gpu_power_watts GPU power usage in watts" >> $METRICS_FILE
    echo "# TYPE node_gpu_power_watts gauge" >> $METRICS_FILE
    echo "node_gpu_power_watts{hostname=\"$HOSTNAME\"} $gpu_power" >> $METRICS_FILE
    
    # Add timestamp
    echo "# HELP node_power_metrics_timestamp Timestamp of the last metrics collection" >> $METRICS_FILE
    echo "# TYPE node_power_metrics_timestamp gauge" >> $METRICS_FILE
    echo "node_power_metrics_timestamp{hostname=\"$HOSTNAME\"} $(date +%s)" >> $METRICS_FILE
    
    # Get Slurm job information if scontrol is available
    if command -v scontrol &> /dev/null; then
        # Get running jobs on this node
        jobs=$(scontrol show jobs -o | grep -i "NodeList=.*$HOSTNAME")
        
        if [ ! -z "$jobs" ]; then
            echo "# HELP slurm_job_power_watts Estimated power usage per Slurm job" >> $METRICS_FILE
            echo "# TYPE slurm_job_power_watts gauge" >> $METRICS_FILE
            
            # Process each job
            echo "$jobs" | while read job; do
                job_id=$(echo "$job" | grep -oP "JobId=\K[0-9]+")
                user_id=$(echo "$job" | grep -oP "UserId=\K[^(]+")
                alloc_cpus=$(echo "$job" | grep -oP "AllocCPUs=\K[0-9]+")
                
                if [ ! -z "$job_id" ] && [ ! -z "$alloc_cpus" ]; then
                    # Calculate job's share of power
                    job_power=$(echo "scale=2; $total_power * ($alloc_cpus / $(nproc))" | bc)
                    echo "slurm_job_power_watts{hostname=\"$HOSTNAME\",job_id=\"$job_id\",user=\"$user_id\"} $job_power" >> $METRICS_FILE
                fi
            done
        fi
    fi
    
    echo "Metrics written to $METRICS_FILE at $(date)"
}

# Run once or continuously
if [ "$1" == "--daemon" ]; then
    echo "Starting continuous collection every $COLLECTION_INTERVAL seconds..."
    while true; do
        collect_and_write_metrics
        sleep $COLLECTION_INTERVAL
    done
else
    # Run once
    collect_and_write_metrics
    echo "Done. To run continuously, use: $0 --daemon"
fi