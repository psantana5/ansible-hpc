# Ansible HPC Inventory Structure
This document describes the inventory structure for the Ansible HPC playbooks. A properly configured inventory is essential for the playbooks to work correctly.

## Directory Structure
The inventory is organized as follows:

plaintext

Open Folder

1

2

3

4

5

6

7

8

9

10

11

/home/psantana/ansible-hpc/inventory/

├── group_vars/

│   ├── all/

│   │   └── main.yml       # Global

variables for all hosts

│   ├── monitoring_servers/ # Variables

specific to monitoring servers

│   │   ├── vars.yml

│   │   └── vault.yml      # Encrypted

sensitive variables

│   ├── nfs/               #

NFS-specific variables

│   └── vault/             # Global

encrypted sensitive variables

│       └── vault.yml

└── hosts                  # Inventory

file defining host groups

Fold

## Hosts File
The hosts file defines all the servers in the HPC cluster, organized into logical groups. Each group corresponds to a specific role or function within the cluster.

### Key Host Groups
- foreman_server : Foreman/Puppet master server
- slurmdbd : Slurm database server
- slurmctld : Slurm controller node
- compute : Compute nodes for running jobs
- login : Login nodes for user access
- ldap_servers : LDAP authentication servers
- monitoring_servers : Prometheus/Grafana monitoring servers
- dns_servers : DNS servers
- nfs_servers : Shared storage servers
- ear_manager : Energy Aware Runtime manager
- ear_nodes : Nodes with EAR monitoring
### Group Hierarchy
The inventory uses Ansible's group hierarchy feature to create parent-child relationships:

plaintext

Open Folder

1

2

3

4

5

6

7

8

9

10

11

12

13

[slurm:children]

slurmdbd

slurmctld

compute

login

[power_monitoring:children]

compute

slurmctld

[ear_nodes:children]

compute

slurmctld

Fold

## Host Variables
Each host should have:

- ansible_host : The IP address of the server
- Optional: ansible_python_interpreter : Path to Python interpreter if needed
Example:

``` ini

services01 ansible_host =192.168.1.152

ansible_python_interpreter =/usr/bin/

python3 grafana_host =192.168.1.152

```

## Group Variables
The group_vars directory contains variables that apply to specific groups:

### Global Variables (all/main.yml)
This file contains variables that apply to all hosts, including:

- Network configuration (domain names, DNS settings)
- Firewall settings
- LDAP configuration
- Slurm cluster configuration
- Monitoring settings
- NFS configuration
- Security settings
- Performance tuning parameters
### Sensitive Variables (Vault Files)
Sensitive data like passwords are stored in encrypted vault files:

- vault/vault.yml : Global sensitive variables
- monitoring_servers/vault.yml : Monitoring-specific sensitive variables
These files are encrypted using Ansible Vault and contain passwords for:

- Database users
- LDAP admin
- Grafana admin
- SMTP services
## Required Configuration
For the playbooks to work correctly, ensure:

1. Host Groups : All servers are assigned to the appropriate groups
2. IP Addresses : All hosts have correct ansible_host values
3. Domain Names : The base_domain variable is set correctly (currently "linkiafp.es")
4. Network Settings : The cluster_network variable matches your actual network (currently "192.168.1.0/24")
5. Vault Passwords : All sensitive variables are properly encrypted and accessible
## Best Practices
1. Use Children Groups : Leverage Ansible's group hierarchy to avoid repetition
2. Encrypt Sensitive Data : Always use Ansible Vault for passwords and keys
3. Validate Variables : Ensure all required variables are defined before running playbooks
4. Host Naming : Use consistent naming conventions for hosts
5. IP Addressing : Maintain a logical IP addressing scheme
## Inventory Validation
Before running playbooks, validate your inventory with:

bash

Run

Open Folder

1

2

ansible-inventory --graph

ansible-inventory --list

This will help identify any issues with the inventory structure before attempting to run playbooks.