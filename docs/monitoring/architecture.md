# HPC Cluster Architecture

## Overview
This document describes the architecture of our HPC cluster deployment.

## Network Topology
```mermaid
graph TD
    Internet[Internet] --> FW[Firewall]
    FW --> DMZ[DMZ Network]
    DMZ --> ForwardProxy[Forward Proxy]
    ForwardProxy --> InternalNet[Internal Network]
    InternalNet --> Foreman[Foreman Server]
    InternalNet --> LDAP[OpenLDAP Server]
    InternalNet --> DNS[DNS Server]
    InternalNet --> SlurmCtl[SLURM Controller]
    InternalNet --> SlurmDB[SLURM Database]
    InternalNet --> Monitoring[Prometheus/Grafana]
    InternalNet --> ComputeNodes[Compute Nodes]