# Slurm-web Installation and Configuration

## Overview

Slurm-web provides a web interface for monitoring and managing your Slurm cluster. This document explains how to deploy Slurm-web using the Ansible role included in this repository.

## Prerequisites

- A functioning Slurm cluster with Slurm >= 23.11
- Slurm accounting enabled
- Supported GNU/Linux distributions (RHEL/CentOS/Rocky Linux, Debian/Ubuntu)

## Deployment

### Using the Provided Playbook

The simplest way to deploy Slurm-web is to use the provided playbook:

```bash
ansible-playbook -i inventory/hosts slurm-web.yml
```

This will install and configure Slurm-web on your login nodes as defined in your inventory.

### Integrating with Existing Playbooks

You can also add the `slurm_web` role to your existing playbooks:

```yaml
- name: Your existing playbook
  hosts: login_nodes
  become: yes
  
  roles:
    - your_existing_role
    - slurm_web
```

## Configuration

The role uses variables defined in `inventory/group_vars/all/main.yml`. The main configuration options are:

```yaml
# Cluster name to display in the web interface
slurm_web_cluster_name: "cluster"

# Service ports
slurm_web_gateway_port: 5011  # Web interface port
slurm_web_agent_port: 5012    # Agent port
```

You can customize these variables in your inventory or playbook as needed.

## Accessing the Web Interface

After successful deployment, you can access the Slurm-web interface at:

```
http://login_node:5011
```

Where `login_node` is the hostname or IP address of your login node.

## Troubleshooting

### Verifying Services

Check if all required services are running:

```bash
systemctl status slurmrestd.service
systemctl status slurm-web-agent.service
systemctl status slurm-web-gateway.service
```

### Testing slurmrestd

Verify that slurmrestd is working correctly:

```bash
curl --unix-socket /run/slurmrestd/slurmrestd.socket http://slurm/slurm/v0.0.40/diag
```

You should receive a JSON response with diagnostic information.

### Checking Logs

Examine service logs for error messages:

```bash
journalctl -u slurmrestd
journalctl -u slurm-web-agent
journalctl -u slurm-web-gateway
```

### Firewall Configuration

Ensure that ports 5011 and 5012 are open in your firewall:

```bash
firewall-cmd --list-ports
```

If they're not listed, you may need to open them:

```bash
firewall-cmd --permanent --add-port=5011/tcp
firewall-cmd --permanent --add-port=5012/tcp
firewall-cmd --reload
```

## References

- [Slurm-web Documentation](https://docs.rackslab.io/slurm-web/)
- [Slurm-web Quickstart Guide](https://docs.rackslab.io/slurm-web/install/quickstart.html)