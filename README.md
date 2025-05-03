[![CI](https://github.com/psantana5/playbooks-slurm/actions/workflows/ci.yml/badge.svg)](https://github.com/psantana5/playbooks-slurm/actions/workflows/ci.yml)

# HPC Cluster Automation with Ansible

This repository provides a comprehensive, modular Ansible-based automation suite for deploying, configuring, and managing a High-Performance Computing (HPC) cluster. It orchestrates all core services required for a modern HPC environment, including compute, storage, authentication, monitoring, reporting, and scientific software management.

## Features

- **Modular Roles:** Each service (SLURM, NFS, LDAP, Monitoring, Reporting, Spack, Containers, etc.) is encapsulated in its own Ansible role for clarity and reusability.
- **Flexible Inventory:** Hosts are grouped by function (compute, login, controller, database, storage, monitoring, etc.) in a central inventory, with group and host variables for fine-grained configuration.
- **Cluster-wide Configuration:** Global variables are managed centrally, ensuring consistency across all nodes.
- **Security Best Practices:** Sensitive data is managed with Ansible Vault; security policies and compliance are considered throughout.
- **Automated Testing:** Includes playbooks for component and integration testing to validate deployments.
- **Extensible Software Management:** Supports both traditional package management and modern scientific software deployment via Spack and containers.
- **Monitoring and Reporting:** Integrates Prometheus, Grafana, and custom reporting scripts for operational visibility.

## Directory Structure
```
playbooks-slurm/
├── ansible.cfg
├── inventory/
│   ├── hosts
│   └── group_vars/
│       ├── all/
│       │   └── main.yml
│       └── ... (other group/host vars)
├── roles/
│   ├── spack/
│   ├── container_apps/
│   ├── monitoring/
│   ├── proxmox_monitoring/
│   ├── slurmctld/
│   ├── slurm_power_monitoring/
│   ├── epel/
│   ├── docker/
│   ├── reporting/
│   └── ... (other roles)
├── playbooks/
│   ├── core/
│   ├── monitoring/
│   └── ... (other playbooks)
├── tests/
│   ├── component_tests/
│   ├── integration_tests/
│   └── ... (test playbooks)
├── scripts/
├── docs/
│   └── monitoring/
│       └── proxmox_power_monitoring.html
├── site.yml
├── spack.yml
└── ... (other files)
```
## Major Components

### SLURM
- Job scheduling, resource management, and accounting for the cluster.
- Power monitoring integration, prolog/epilog scripts, and SLURM group management.

### NFS
- Shared storage for home directories, applications, and scratch space.
- Secure exports, performance tuning, and automated fstab management.

### LDAP
- Centralized authentication and user/group management.
- TLS support, replication, and integration with SSSD.

### Monitoring
- Cluster health and performance monitoring using Prometheus and Grafana.
- Node exporter, SLURM exporter, Proxmox power monitoring, and custom dashboards.

### Reporting
- Automated generation and collection of usage and efficiency reports.

### Spack
- Scientific software management and environment setup.
- Automated installation, environment sourcing, and customizable install location/version.

### Container Apps
- Deployment of scientific applications in containers (Singularity/Apptainer).
- Pulls common scientific images, creates SLURM submission scripts.

### Proxmox Monitoring
- Collects and visualizes power metrics from Proxmox nodes.
- Custom scripts, systemd services, and Grafana dashboard deployment.

## Inventory & Variable Management

- Hosts are grouped by function (e.g., `[compute]`, `[login]`, `[slurmctld]`, `[nfs_servers]`, `[monitoring_servers]`, etc.).
- Centralized group and host variables for easy customization.
- Global variables for cluster-wide settings (timezone, domain, firewall, LDAP, SLURM, monitoring, backup, security, etc.).

## Security

- Sensitive variables managed with Ansible Vault.
- Security policy and compliance options (SELinux, firewalld, fail2ban, password policies, audit logging).

## Testing

- Component and integration tests to validate deployments and workflows.
- Playbooks for setting up and tearing down test environments.

## Usage Workflow

1. **Configure Inventory:** Define all hosts and groups in `inventory/hosts` and set group/host variables as needed.
2. **Customize Variables:** Adjust global and role-specific variables in `group_vars` and `defaults/main.yml` files.
3. **Run Playbooks:** Use playbooks (e.g., `site.yml`, `spack.yml`, `proxmox-monitoring.yml`) to deploy or update services across the cluster.
4. **Test and Validate:** Use the `tests/` playbooks to verify correct deployment and operation.
5. **Monitor and Report:** Access Grafana dashboards and reporting outputs for cluster health and usage insights.

## Maintenance & Best Practices

- Regular updates and security patches.
- Automated backup strategies for SLURM DB, LDAP, and configuration files.
- Continuous monitoring and alerting for system health and performance.
- Up-to-date documentation for onboarding and troubleshooting.

## Contribution & Collaboration

- Contribution guidelines and code of conduct are included in the repository.
- Use issues and pull requests for collaboration and improvements.

---

