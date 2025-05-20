#!/usr/bin/env python3

"""
GitHub Copilot Integration for Repository Analyzer

This module integrates GitHub Copilot with the repository analyzer,
allowing it to automatically implement improvement suggestions.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Import the repository analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from repo_analyzer import RepoAnalyzer, REPO_ROOT

class CopilotIntegration:
    """Handles GitHub Copilot integration for repository analyzer suggestions."""
    
    def __init__(self, repo_path=REPO_ROOT, token=None):
        self.repo_path = repo_path
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.analyzer = RepoAnalyzer(output_format='json')
        
    def get_suggestions(self, role=None, category=None):
        """Get suggestions from the repository analyzer."""
        # Set filters if provided
        if role:
            self.analyzer.filter_role = role
        if category:
            self.analyzer.filter_category = category
            
        # Run analysis
        return self.analyzer.analyze()
    
    def generate_improvements(self, suggestions, output_dir=None, dry_run=False):
        """Generate improvements using GitHub Copilot."""
        if not output_dir:
            output_dir = os.path.join(self.repo_path, 'copilot_improvements')
            os.makedirs(output_dir, exist_ok=True)
            
        print(f"Generating improvements for {len(suggestions)} suggestions...")
        
        improvements = []
        for idx, suggestion in enumerate(suggestions):
            print(f"\nProcessing suggestion {idx+1}/{len(suggestions)}: {suggestion['title']}")
            
            # Create a prompt for Copilot
            prompt = self._create_copilot_prompt(suggestion)
            
            # Save the prompt to a file
            prompt_file = os.path.join(output_dir, f"prompt_{idx+1}.md")
            with open(prompt_file, 'w') as f:
                f.write(prompt)
                
            # Generate improvement using Copilot CLI if not in dry run mode
            if not dry_run:
                improvement = self._call_copilot(prompt, suggestion)
                improvements.append({
                    'suggestion': suggestion,
                    'improvement': improvement,
                    'prompt_file': prompt_file
                })
                
                # Save the improvement to a file
                improvement_file = os.path.join(output_dir, f"improvement_{idx+1}.md")
                with open(improvement_file, 'w') as f:
                    f.write(improvement)
                    
                print(f"Improvement saved to: {improvement_file}")
            else:
                print(f"Dry run: Prompt saved to {prompt_file}")
                
        return improvements
    
    def _create_copilot_prompt(self, suggestion):
        """Create a prompt for GitHub Copilot based on the suggestion."""
        prompt = f"# Ansible HPC Repository Improvement\n\n"
        prompt += f"## Suggestion: {suggestion['title']}\n\n"
        prompt += f"**Priority:** {suggestion['priority'].upper()}\n\n"
        prompt += f"**Category:** {suggestion['category']}\n\n"
        prompt += f"{suggestion['description']}\n\n"
        
        prompt += "**Files to modify:**\n"
        for path in suggestion['file_paths']:
            rel_path = os.path.relpath(path, self.repo_path)
            prompt += f"- `{rel_path}`\n"
            
            # Add file content if it exists
            if os.path.isfile(path):
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                    prompt += f"\n```\n{content}\n```\n\n"
                except Exception as e:
                    prompt += f"\nError reading file: {e}\n\n"
        
        prompt += "\n## Task\n\n"
        prompt += "Please implement the suggested improvement for the Ansible HPC repository. "
        prompt += "Provide the complete modified file(s) with your changes.\n\n"
        
        return prompt
    
    def _call_copilot(self, prompt, suggestion):
        """Call GitHub Copilot CLI to generate an improvement."""
        # This is a placeholder for the actual Copilot CLI integration
        # In a real implementation, this would use the Copilot API or CLI
        
        # For now, we'll generate a simple improvement based on the suggestion type
        improvement = f"# Improvement for: {suggestion['title']}\n\n"
        
        if suggestion['category'] == 'documentation':
            improvement += self._generate_documentation_improvement(suggestion)
        elif suggestion['category'] == 'best_practices':
            improvement += self._generate_best_practices_improvement(suggestion)
        elif suggestion['category'] == 'role_completeness':
            improvement += self._generate_role_completeness_improvement(suggestion)
        else:
            improvement += f"Placeholder improvement for {suggestion['category']} category.\n"
            improvement += f"This would be generated by GitHub Copilot in a real implementation.\n"
        
        return improvement
    
    def _generate_documentation_improvement(self, suggestion):
        """Generate a documentation improvement."""
        improvement = "## Documentation Improvement\n\n"
        
        if 'README.md' in str(suggestion['file_paths'][0]):
            improvement += "Here's an improved README.md with the missing sections:\n\n"
            improvement += "```markdown\n"
            improvement += "# Role Name\n\n"
            improvement += "A brief description of the role goes here.\n\n"
            improvement += "## Requirements\n\n"
            improvement += "Any pre-requisites that may not be covered by Ansible itself or the role.\n\n"
            improvement += "## Role Variables\n\n"
            improvement += "A description of the settable variables for this role.\n\n"
            improvement += "## Dependencies\n\n"
            improvement += "A list of other roles hosted on Galaxy should go here.\n\n"
            improvement += "## Example Playbook\n\n"
            improvement += "```yaml\n- hosts: servers\n  roles:\n    - role_name\n```\n\n"
            improvement += "## License\n\n"
            improvement += "MIT\n\n"
            improvement += "## Author Information\n\n"
            improvement += "An optional section for the role authors.\n"
            improvement += "```\n"
        
        return improvement
    
    def _generate_best_practices_improvement(self, suggestion):
        """Generate a best practices improvement."""
        improvement = "## Best Practices Improvement\n\n"
        
        if 'hardcoded' in suggestion['title'].lower():
            improvement += "Replace hardcoded values with variables:\n\n"
            improvement += "```yaml\n"
            improvement += "# Before\n"
            improvement += "- name: Configure service\n"
            improvement += "  template:\n"
            improvement += "    src: service.conf.j2\n"
            improvement += "    dest: /etc/service.conf\n\n"
            improvement += "# After\n"
            improvement += "- name: Configure service\n"
            improvement += "  template:\n"
            improvement += "    src: service.conf.j2\n"
            improvement += "    dest: \"{{ service_config_path }}\"\n"
            improvement += "```\n\n"
            improvement += "Add these variables to defaults/main.yml:\n\n"
            improvement += "```yaml\n"
            improvement += "# Service configuration\n"
            improvement += "service_config_path: /etc/service.conf\n"
            improvement += "```\n"
        
        return improvement
    
    def _generate_role_completeness_improvement(self, suggestion):
        """Generate a role completeness improvement."""
        improvement = "## Role Completeness Improvement\n\n"
        
        if 'missing standard directories' in suggestion['description'].lower():
            improvement += "Create the missing directories with appropriate files:\n\n"
            
            if 'meta' in suggestion['description'].lower():
                improvement += "### meta/main.yml\n\n"
                improvement += "```yaml\n"
                improvement += "---\n"
                improvement += "dependencies: []\n\n"
                improvement += "galaxy_info:\n"
                improvement += "  author: your_name\n"
                improvement += "  description: your_description\n"
                improvement += "  company: your_company\n"
                improvement += "  license: MIT\n"
                improvement += "  min_ansible_version: 2.9\n"
                improvement += "  platforms:\n"
                improvement += "    - name: EL\n"
                improvement += "      versions:\n"
                improvement += "        - 7\n"
                improvement += "        - 8\n"
                improvement += "  galaxy_tags: []\n"
                improvement += "```\n\n"
            
            if 'defaults' in suggestion['description'].lower():
                improvement += "### defaults/main.yml\n\n"
                improvement += "```yaml\n"
                improvement += "---\n"
                improvement += "# defaults file\n"
                improvement += "```\n\n"
            
            if 'handlers' in suggestion['description'].lower():
                improvement += "### handlers/main.yml\n\n"
                improvement += "```yaml\n"
                improvement += "---\n"
                improvement += "# handlers file\n"
                improvement += "```\n\n"
            
            if 'vars' in suggestion['description'].lower():
                improvement += "### vars/main.yml\n\n"
                improvement += "```yaml\n"
                improvement += "---\n"
                improvement += "# vars file\n"
                improvement += "```\n\n"
            
            if 'templates' in suggestion['description'].lower():
                improvement += "### Create templates directory\n\n"
                improvement += "```bash\n"
                improvement += "mkdir -p templates\n"
                improvement += "```\n"
        
        return improvement

def main():
    """Main function to run the Copilot integration."""
    parser = argparse.ArgumentParser(description='GitHub Copilot Integration for Repository Analyzer')
    parser.add_argument('--role', help='Only analyze a specific role')
    parser.add_argument('--category', help='Only analyze a specific category')
    parser.add_argument('--output-dir', help='Directory to save improvements')
    parser.add_argument('--token', help='GitHub token for authentication')
    parser.add_argument('--dry-run', action='store_true', help='Only generate prompts, do not call Copilot')
    
    args = parser.parse_args()
    
    # Initialize Copilot integration
    copilot = CopilotIntegration(token=args.token)
    
    # Get suggestions
    suggestions = copilot.get_suggestions(role=args.role, category=args.category)
    
    if not suggestions:
        print("No suggestions found.")
        return
    
    # Generate improvements
    copilot.generate_improvements(suggestions, output_dir=args.output_dir, dry_run=args.dry_run)

if __name__ == '__main__':
    main()