# Autofs Role

This Ansible role configures and manages the autofs service for automatic mounting of NFS filesystems.

## Description

The autofs role sets up automatic filesystem mounting using the autofs service. It configures:
- Home directory mounts (`/home`)
- Application directory mounts (`/apps`)
- Automatic mounting and unmounting of NFS shares

## Requirements

- Ansible 2.9 or higher
- Target system must be running a supported Linux distribution
- NFS server must be accessible
- Root or sudo privileges

## Role Variables

Available variables are listed below, along with default values:

```yaml
# NFS server hostname
nfs_server_host: filer01

# Autofs mount configurations
autofs_mounts:
  - name: home
    path: /home
    options: "-rw,soft,intr,rsize=32768,wsize=32768"
    source: "{{ nfs_server_host }}:/home/&"
  - name: apps
    path: /apps
    options: "-ro,soft,intr,rsize=32768,wsize=32768"
    source: "{{ nfs_server_host }}:/apps/&"
```

## Dependencies

- nfs_client role (for NFS client utilities)

## Example Playbook

```yaml
- hosts: clients
  roles:
    - role: autofs
      vars:
        nfs_server_host: nfs.example.com
```

## License

MIT

## Author Information

Pau Santana 