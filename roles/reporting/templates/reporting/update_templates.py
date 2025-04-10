#!/usr/bin/env python3
import os
import re

# Directory containing the templates
template_dir = "/home/psantana/playbooks-slurm/roles/reporting/templates/reporting"

# Ansible variables to look for and update
ansible_vars = [
    "admin_email",
    "base_domain",
    "cpu_hour_rate",
    "gpu_hour_rate",
    "mem_gb_hour_rate",
    "currency_symbol",
    "smtp_from",
    "smtp_server",
    "smtp_port",
    "smtp_use_tls",
    "smtp_username",
    "smtp_password"
]

# Process each template file
for filename in os.listdir(template_dir):
    if filename.endswith(".py.j2"):
        filepath = os.path.join(template_dir, filename)
        print(f"Processing {filepath}")
        
        # Read the file content
        with open(filepath, 'r') as file:
            content = file.read()
        
        # Replace Ansible variables with the new delimiter format
        for var in ansible_vars:
            # Match patterns like {{ var }} or {{ var | default(...) }}
            pattern = r'{{\s*' + var + r'(\s*\|\s*[^}]+)?\s*}}'
            replacement = r'{{{{ ' + var + r'\1 }}}}'
            content = re.sub(pattern, replacement, content)
        
        # Write the updated content back to the file
        with open(filepath, 'w') as file:
            file.write(content)
        
        print(f"Updated {filepath}")

print("All template files have been updated!")