# HPC Cluster Deployment with Ansible

## This repository contains Ansible playbooks and roles for deploying and configuring a complete High-Performance Computing (HPC) cluster with SLURM workload manager, OpenLDAP authentication, and monitoring infrastructure.

🏗️ Architecture Overview
The infrastructure consists of the following components:

SLURM Cluster
Controller Node (slurmctld)

Database Node (slurmdbd with MariaDB)

Compute Nodes (slurmd)

Authentication
OpenLDAP Server

LDAP Clients (SSSD)

Monitoring
Prometheus

Grafana

Node Exporter

SLURM Exporter

Additional Services
DNS Server

Foreman for system management

Docker for containerized services

📁 Directory Structure
graphql
Kopiera
Redigera
playbooks-ansible/
├── inventory/
│ └── hosts # Inventory file
├── group_vars/
│ ├── all.yml # Global variables
│ └── vault.yml # Encrypted sensitive variables
├── roles/
│ ├── compute/ # SLURM compute nodes
│ ├── dns/ # DNS configuration
│ ├── docker/ # Docker installation
│ ├── epel/ # EPEL repository
│ ├── foreman/ # Foreman setup
│ ├── grafana/ # Grafana configuration
│ ├── monitoring/ # Monitoring stack
│ ├── node_exporter/ # Prometheus Node Exporter
│ ├── openldap/ # OpenLDAP server
│ ├── prometheus/ # Prometheus configuration
│ ├── slurmctld/ # SLURM controller
│ └── slurmdbd/ # SLURM database
├── templates/
│ ├── ldap.conf.j2 # LDAP client template
│ └── sssd.conf.j2 # SSSD configuration template
├── compute.yml # Playbook for compute nodes
├── deploy-foreman.yml # Playbook for Foreman
├── dns.yml # Playbook for DNS
├── ldap-client.yml # Playbook for LDAP clients
├── monitoring.yml # Playbook for monitoring stack
├── openldap.yml # Playbook for OpenLDAP
├── site.yml # Main playbook
├── slurmctld.yml # SLURM controller playbook
├── slurmdbd.yml # SLURM database playbook
└── documentacion_slurm.tex # LaTeX documentation for SLURM
🚀 Deployment Order
To ensure a correct deployment, follow this order:

Basic infrastructure (DNS, EPEL)

Authentication (OpenLDAP)

SLURM components (in order: slurmdbd → slurmctld → compute)

Monitoring stack

Additional services (Foreman, Docker)

📜 Playbooks
Main Playbooks
site.yml: Orchestrates the entire deployment

slurmctld.yml: Deploys the SLURM controller node

slurmdbd.yml: Deploys the SLURM database node

compute.yml: Configures SLURM compute nodes

openldap.yml: Sets up the OpenLDAP server

ldap-client.yml: Configures LDAP clients (SSSD)

monitoring.yml: Deploys Prometheus and Grafana

dns.yml: Sets up the DNS server

deploy-foreman.yml: Installs and configures Foreman

⚙️ Configuration
All configuration is centralized in inventory/group_vars/all.yml and includes:

Network and domain settings

SLURM cluster configuration

OpenLDAP settings

Database credentials (from encrypted vault.yml)

Monitoring configuration

Firewall rules

SSH settings

Backup policies

SLURM user/group management

Sensitive information is stored securely in an encrypted Ansible vault.

⚡ SLURM Cluster
The SLURM cluster includes:

Controller Node: Manages job scheduling and resource allocation

Database Node: Stores job/accounting data using MariaDB

Compute Nodes: Execute jobs submitted via SLURM

Includes:

Munge authentication

SLURM configuration

User/group setup

Firewall rules

🔐 Authentication
Centralized user authentication with OpenLDAP:

Centralized user/group management

Group-based access control

SSSD integration on all nodes

Automatic home directory creation

📈 Monitoring
The monitoring stack includes:

Prometheus: Metrics collection

Grafana: Dashboards and visualizations

Node Exporter: Node metrics

SLURM Exporter: SLURM-specific metrics

▶️ Usage
Deploy the Entire Infrastructure
bash
Kopiera
Redigera
ansible-playbook -i inventory/hosts site.yml
Deploy Individual Components
bash
Kopiera
Redigera
ansible-playbook -i inventory/hosts <playbook>.yml
✅ Requirements
Ansible 2.9+

SSH access to all nodes

Sudo privileges on target nodes

Rocky Linux 8+ (or compatible)

🔒 Security Considerations
Sensitive variables are encrypted via Ansible Vault

SSH keys used for authentication

Firewall rules configured for each service

LDAP can be configured with TLS encryption

🛠️ Maintenance
Regular tasks to ensure system health:

Backup SLURM database

Monitor system resources

Update packages

Review logs for errors

Check SLURM job accounting

📚 Documentation
documentacion_slurm.tex: Full SLURM deployment documentation in LaTeX format
