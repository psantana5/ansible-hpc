#!/usr/bin/env python3
"""
Power Management Metrics Collector for Slurm Cluster
Collects power data and writes it to a file for node_exporter textfile collector
"""

import subprocess
import time
import os
import logging
import json
import re
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/var/log/power_metrics.log'
)
logger = logging.getLogger('power_metrics')

# Configuration
METRICS_FILE = '/var/lib/node_exporter/textfile_collector/power_metrics.prom'
COLLECTION_INTERVAL = 60  # seconds
HOSTNAME = os.uname().nodename

def get_cpu_info():
    """Get CPU information"""
    try:
        # Get CPU model
        with open('/proc/cpuinfo', 'r') as f:
            cpu_info = f.read()
        
        model_name = re.search(r'model name\s+:\s+(.*)', cpu_info)
        if model_name:
            return model_name.group(1)
        return "Unknown CPU"
    except Exception as e:
        logger.error(f"Error getting CPU info: {e}")
        return "Unknown CPU"

def get_cpu_power():
    """
    Get CPU power consumption using RAPL (Running Average Power Limit)
    This works on Intel CPUs with RAPL support
    """
    try:
        # Check if RAPL is available
        rapl_path = '/sys/class/powercap/intel-rapl'
        if not os.path.exists(rapl_path):
            logger.warning("RAPL not available, using estimation")
            return estimate_cpu_power()
        
        # Read energy values from all CPU domains
        total_power = 0
        for domain in os.listdir(rapl_path):
            if domain.startswith('intel-rapl:'):
                energy_file = f"{rapl_path}/{domain}/energy_uj"
                if os.path.exists(energy_file):
                    with open(energy_file, 'r') as f:
                        energy_before = int(f.read().strip())
                    
                    # Wait a short time to measure power
                    time.sleep(1)
                    
                    with open(energy_file, 'r') as f:
                        energy_after = int(f.read().strip())
                    
                    # Convert microjoules to watts (joules per second)
                    power = (energy_after - energy_before) / 1000000
                    total_power += power
        
        if total_power > 0:
            return total_power
        else:
            return estimate_cpu_power()
    except Exception as e:
        logger.error(f"Error reading RAPL: {e}")
        return estimate_cpu_power()

def estimate_cpu_power():
    """Estimate CPU power based on load"""
    try:
        # Get CPU load
        with open('/proc/loadavg', 'r') as f:
            load = float(f.read().split()[0])
        
        # Get number of CPUs
        cpu_count = os.cpu_count()
        
        # Calculate load percentage
        load_percent = min(100, (load / cpu_count) * 100)
        
        # Estimate power: base power + additional power based on load
        # These values should be adjusted based on your specific CPU model
        base_power = 10  # Watts at idle
        max_additional_power = 90  # Additional watts at 100% load
        
        estimated_power = base_power + (max_additional_power * load_percent / 100)
        return estimated_power
    except Exception as e:
        logger.error(f"Error estimating CPU power: {e}")
        return 50  # Default fallback value

def get_memory_power():
    """Estimate memory power consumption"""
    try:
        # Get memory info
        with open('/proc/meminfo', 'r') as f:
            mem_info = f.read()
        
        # Parse total and free memory
        total = re.search(r'MemTotal:\s+(\d+)', mem_info)
        available = re.search(r'MemAvailable:\s+(\d+)', mem_info)
        
        if total and available:
            total_kb = int(total.group(1))
            available_kb = int(available.group(1))
            used_kb = total_kb - available_kb
            
            # Calculate usage percentage
            usage_percent = (used_kb / total_kb) * 100
            
            # Estimate power: base power + additional power based on usage
            # These values should be adjusted based on your specific memory configuration
            base_power = 5  # Watts at idle
            max_additional_power = 15  # Additional watts at 100% usage
            
            estimated_power = base_power + (max_additional_power * usage_percent / 100)
            return estimated_power
        else:
            return 10  # Default fallback value
    except Exception as e:
        logger.error(f"Error estimating memory power: {e}")
        return 10  # Default fallback value

def get_gpu_power():
    """Get GPU power consumption if available"""
    try:
        # Try to use nvidia-smi for NVIDIA GPUs
        result = subprocess.run(['nvidia-smi', '--query-gpu=power.draw', '--format=csv,noheader,nounits'], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            powers = result.stdout.strip().split('\n')
            total_power = sum(float(p) for p in powers if p.strip())
            return total_power
        else:
            return 0  # No NVIDIA GPU or nvidia-smi not available
    except Exception as e:
        logger.debug(f"No NVIDIA GPU detected: {e}")
        return 0

def get_slurm_job_info():
    """Get information about running Slurm jobs on this node"""
    try:
        result = subprocess.run(['scontrol', 'show', 'jobs', '-o'], capture_output=True, text=True)
        if result.returncode == 0:
            jobs_data = result.stdout.strip()
            jobs = []
            
            # Parse job information
            for job_str in jobs_data.split('\n'):
                if not job_str:
                    continue
                    
                job = {}
                for item in job_str.split():
                    if '=' in item:
                        key, value = item.split('=', 1)
                        job[key] = value
                
                # Check if this job is running on the current node
                if 'NodeList' in job and HOSTNAME in job['NodeList']:
                    jobs.append(job)
            
            return jobs
        else:
            logger.warning("Failed to get Slurm job information")
            return []
    except Exception as e:
        logger.error(f"Error getting Slurm job info: {e}")
        return []

def collect_power_data():
    """Collect all power data and return metrics"""
    try:
        # Get power data from different components
        cpu_power = get_cpu_power()
        memory_power = get_memory_power()
        gpu_power = get_gpu_power()
        
        # Calculate total power
        total_power = cpu_power + memory_power + gpu_power
        
        # Get Slurm job information
        jobs = get_slurm_job_info()
        
        # Create metrics
        metrics = []
        
        # Add node power metrics
        metrics.append(f'node_power_usage_watts{{hostname="{HOSTNAME}"}} {total_power}')
        metrics.append(f'node_cpu_power_watts{{hostname="{HOSTNAME}"}} {cpu_power}')
        metrics.append(f'node_memory_power_watts{{hostname="{HOSTNAME}"}} {memory_power}')
        metrics.append(f'node_gpu_power_watts{{hostname="{HOSTNAME}"}} {gpu_power}')
        
        # Add job-specific metrics if jobs are running
        for job in jobs:
            if 'JobId' in job:
                job_id = job['JobId']
                # Estimate job power based on CPU allocation
                if 'NumCPUs' in job and 'AllocCPUs' in job:
                    num_cpus = int(job['NumCPUs'])
                    alloc_cpus = int(job['AllocCPUs'])
                    
                    # Calculate job's share of power
                    if os.cpu_count() > 0:
                        job_power = total_power * (alloc_cpus / os.cpu_count())
                        metrics.append(f'slurm_job_power_watts{{hostname="{HOSTNAME}",job_id="{job_id}",user="{job.get("UserId", "unknown")}"}} {job_power}')
        
        # Add timestamp
        metrics.append(f'node_power_metrics_timestamp{{hostname="{HOSTNAME}"}} {int(time.time())}')
        
        return metrics
    except Exception as e:
        logger.error(f"Error collecting power data: {e}")
        return []

def write_metrics_to_file(metrics):
    """Write metrics to file for node_exporter textfile collector"""
    try:
        with open(METRICS_FILE, 'w') as f:
            f.write('\n'.join(metrics) + '\n')
        logger.debug(f"Wrote {len(metrics)} metrics to {METRICS_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error writing metrics to file: {e}")
        return False

def main():
    logger.info("Starting power metrics collector")
    
    while True:
        try:
            # Collect power data
            metrics = collect_power_data()
            
            # Write metrics to file
            if metrics:
                write_metrics_to_file(metrics)
            
            # Wait for next collection cycle
            time.sleep(COLLECTION_INTERVAL)
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(10)  # Wait a bit before retrying

if __name__ == "__main__":
    main()