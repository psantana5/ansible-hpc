# Slurm-web Role

This Ansible role installs and configures Slurm-web, a web interface for Slurm workload manager based on the [Rackslab documentation](https://docs.rackslab.io/slurm-web/install/quickstart.html).

## Requirements

- A functioning Slurm cluster with Slurm >= 23.11 and accounting enabled
- Supported GNU/Linux distributions (RHEL/CentOS/Rocky Linux, Debian/Ubuntu)

## Role Variables

The following variables can be configured in your playbook or inventory:

```yaml
# Cluster name to display in the web interface
slurm_web_cluster_name: "cluster"

# Service ports
slurm_web_gateway_port: 5011  # Web interface port
slurm_web_agent_port: 5012    # Agent port

# Installation options
slurm_web_install_epel: true  # Install EPEL repository on RedHat systems if needed
```

## Dependencies

- Requires a functioning Slurm installation
- EPEL repository for RedHat-based systems (automatically installed if `slurm_web_install_epel` is true)

## Example Playbook

```yaml
---
- name: Deploy Slurm-web Interface
  hosts: login_nodes
  become: yes
  
  roles:
    - slurm_web
```

## Usage

After installation, access the Slurm-web interface at: `http://<host_ip>:5011`

## Troubleshooting

If you encounter issues with the installation or configuration:

1. Check the service status:
   ```bash
   systemctl status slurmrestd.service
   systemctl status slurm-web-agent.service
   systemctl status slurm-web-gateway.service
   ```

2. Verify slurmrestd is working correctly:
   ```bash
   curl --unix-socket /run/slurmrestd/slurmrestd.socket http://<host_ip>/slurm/v0.0.40/diag
   ```

3. Check the logs:
   ```bash
   journalctl -u slurmrestd
   journalctl -u slurm-web-agent
   journalctl -u slurm-web-gateway
   ```

## License

GPL-3.0-or-later

## Author Information

Created for the ansible-hpc project.