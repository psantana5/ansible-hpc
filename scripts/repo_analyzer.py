#!/usr/bin/env python3

"""
Repository Analyzer for ansible-hpc

This script analyzes the ansible-hpc repository structure, identifies potential improvements,
and generates suggestions that can be submitted as GitHub issues or branches.
"""

import os
import sys
import re
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLES_DIR = os.path.join(REPO_ROOT, 'roles')
PLAYBOOKS_DIR = os.path.join(REPO_ROOT, 'playbooks')
TESTS_DIR = os.path.join(REPO_ROOT, 'tests')

# Analysis categories
CATEGORIES = {
    'documentation': 'Documentation improvements',
    'best_practices': 'Ansible best practices',
    'role_completeness': 'Role structure completeness',
    'testing': 'Test coverage',
    'security': 'Security enhancements',
    'performance': 'Performance optimizations',
    'maintenance': 'Maintenance and updates'
}

class RepoAnalyzer:
    """Analyzes the ansible-hpc repository and generates improvement suggestions."""
    
    def __init__(self, output_format='console', github_integration=False, copilot_integration=False):
        self.output_format = output_format
        self.github_integration = github_integration
        self.copilot_integration = copilot_integration
        self.suggestions = []
        self.roles = self._get_roles()
        self.playbooks = self._get_playbooks()
        self.filter_role = None
        self.filter_category = None
        
    def _get_roles(self):
        """Get all roles in the repository."""
        return [d for d in os.listdir(ROLES_DIR) 
                if os.path.isdir(os.path.join(ROLES_DIR, d))]
    
    def _get_playbooks(self):
        """Get all playbooks in the repository."""
        playbooks = []
        for root, _, files in os.walk(PLAYBOOKS_DIR):
            for file in files:
                if file.endswith('.yml'):
                    playbooks.append(os.path.join(root, file))
        return playbooks + [f for f in os.listdir(REPO_ROOT) 
                           if f.endswith('.yml') and os.path.isfile(os.path.join(REPO_ROOT, f))]
    
    def analyze(self):
        """Run all analysis methods."""
        self.analyze_role_structure()
        self.analyze_documentation()
        self.analyze_best_practices()
        self.analyze_testing()
        self.analyze_security()
        self.analyze_dependencies()
        
        # Apply filters if set
        filtered_suggestions = self.suggestions
        
        # Filter by role if specified
        if self.filter_role:
            filtered_suggestions = [s for s in filtered_suggestions 
                                   if any(self.filter_role in path for path in s['file_paths'])]
        
        # Filter by category if specified
        if self.filter_category:
            filtered_suggestions = [s for s in filtered_suggestions 
                                   if s['category'] == self.filter_category]
        
        return filtered_suggestions
    
    def analyze_role_structure(self):
        """Check if roles follow the standard Ansible role structure."""
        standard_dirs = ['defaults', 'handlers', 'meta', 'tasks', 'templates', 'vars']
        
        for role in self.roles:
            role_path = os.path.join(ROLES_DIR, role)
            existing_dirs = [d for d in os.listdir(role_path) 
                            if os.path.isdir(os.path.join(role_path, d))]
            
            # Check for missing directories
            missing_dirs = [d for d in standard_dirs if d not in existing_dirs]
            if missing_dirs:
                self.add_suggestion(
                    category='role_completeness',
                    title=f"Complete directory structure for '{role}' role",
                    description=f"The '{role}' role is missing standard directories: {', '.join(missing_dirs)}. "
                                f"Consider adding these directories to follow Ansible role conventions.",
                    file_paths=[role_path],
                    priority='medium'
                )
            
            # Check for README.md
            if not os.path.exists(os.path.join(role_path, 'README.md')):
                self.add_suggestion(
                    category='documentation',
                    title=f"Add README.md for '{role}' role",
                    description=f"The '{role}' role is missing a README.md file. "
                                f"Adding documentation will help users understand the role's purpose and usage.",
                    file_paths=[role_path],
                    priority='high'
                )
            
            # Check for meta/main.yml
            meta_path = os.path.join(role_path, 'meta', 'main.yml')
            if not os.path.exists(meta_path):
                self.add_suggestion(
                    category='role_completeness',
                    title=f"Add meta/main.yml for '{role}' role",
                    description=f"The '{role}' role is missing meta/main.yml. "
                                f"This file is important for role metadata and dependencies.",
                    file_paths=[role_path],
                    priority='medium'
                )
    
    def analyze_documentation(self):
        """Analyze documentation quality and completeness."""
        # Check main README.md
        readme_path = os.path.join(REPO_ROOT, 'README.md')
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as f:
                content = f.read()
                
                # Check for common sections
                missing_sections = []
                if not re.search(r'#+\s*Requirements', content, re.IGNORECASE):
                    missing_sections.append('Requirements')
                if not re.search(r'#+\s*Installation', content, re.IGNORECASE):
                    missing_sections.append('Installation')
                if not re.search(r'#+\s*Usage', content, re.IGNORECASE):
                    missing_sections.append('Usage')
                
                if missing_sections:
                    self.add_suggestion(
                        category='documentation',
                        title="Enhance main README.md with additional sections",
                        description=f"The main README.md could be improved by adding these sections: {', '.join(missing_sections)}.",
                        file_paths=[readme_path],
                        priority='medium'
                    )
        
        # Check role READMEs
        for role in self.roles:
            readme_path = os.path.join(ROLES_DIR, role, 'README.md')
            if os.path.exists(readme_path):
                with open(readme_path, 'r') as f:
                    content = f.read()
                    
                    # Check for common role documentation sections
                    missing_sections = []
                    if not re.search(r'#+\s*Requirements', content, re.IGNORECASE):
                        missing_sections.append('Requirements')
                    if not re.search(r'#+\s*Role Variables', content, re.IGNORECASE):
                        missing_sections.append('Role Variables')
                    if not re.search(r'#+\s*Dependencies', content, re.IGNORECASE):
                        missing_sections.append('Dependencies')
                    if not re.search(r'#+\s*Example Playbook', content, re.IGNORECASE):
                        missing_sections.append('Example Playbook')
                    
                    if missing_sections:
                        self.add_suggestion(
                            category='documentation',
                            title=f"Enhance README.md for '{role}' role",
                            description=f"The README.md for '{role}' role could be improved by adding these sections: {', '.join(missing_sections)}.",
                            file_paths=[readme_path],
                            priority='medium'
                        )
    
    def analyze_best_practices(self):
        """Check if the repository follows Ansible best practices."""
        # Check for hardcoded values that should be variables
        for role in self.roles:
            tasks_dir = os.path.join(ROLES_DIR, role, 'tasks')
            if os.path.exists(tasks_dir):
                for file in os.listdir(tasks_dir):
                    if file.endswith('.yml'):
                        file_path = os.path.join(tasks_dir, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                            
                            # Look for hardcoded IPs, ports, paths, etc.
                            ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
                            port_pattern = r':\d{2,5}\b'
                            
                            if re.search(ip_pattern, content):
                                self.add_suggestion(
                                    category='best_practices',
                                    title=f"Replace hardcoded IPs in '{role}/{file}'",
                                    description=f"Found hardcoded IP addresses in '{role}/{file}'. "
                                                f"Consider replacing them with variables for better maintainability.",
                                    file_paths=[file_path],
                                    priority='high'
                                )
                            
                            if re.search(port_pattern, content):
                                # Check if it's not already a variable
                                if not re.search(r':\{\{.*\}\}', content):
                                    self.add_suggestion(
                                        category='best_practices',
                                        title=f"Replace hardcoded ports in '{role}/{file}'",
                                        description=f"Found hardcoded ports in '{role}/{file}'. "
                                                    f"Consider replacing them with variables for better maintainability.",
                                        file_paths=[file_path],
                                        priority='medium'
                                    )
        
        # Check for tags usage
        for role in self.roles:
            tasks_dir = os.path.join(ROLES_DIR, role, 'tasks')
            if os.path.exists(tasks_dir):
                main_file = os.path.join(tasks_dir, 'main.yml')
                if os.path.exists(main_file):
                    with open(main_file, 'r') as f:
                        content = f.read()
                        if 'tags:' not in content:
                            self.add_suggestion(
                                category='best_practices',
                                title=f"Add tags to '{role}' role tasks",
                                description=f"The tasks in '{role}' role don't use tags. "
                                            f"Adding tags would improve playbook flexibility and selective execution.",
                                file_paths=[main_file],
                                priority='low'
                            )
    
    def analyze_testing(self):
        """Check for test coverage and testing best practices."""
        # Check if roles have corresponding tests
        for role in self.roles:
            test_paths = [
                os.path.join(TESTS_DIR, 'component_tests', f"{role}_tests.yml"),
                os.path.join(TESTS_DIR, 'integration_tests', f"{role}_integration_tests.yml")
            ]
            
            if not any(os.path.exists(p) for p in test_paths):
                self.add_suggestion(
                    category='testing',
                    title=f"Add tests for '{role}' role",
                    description=f"The '{role}' role doesn't have dedicated tests. "
                                f"Consider adding component and integration tests to ensure reliability.",
                    file_paths=[os.path.join(ROLES_DIR, role)],
                    priority='high'
                )
        
        # Check for molecule tests
        for role in self.roles:
            molecule_dir = os.path.join(ROLES_DIR, role, 'molecule')
            if not os.path.exists(molecule_dir):
                self.add_suggestion(
                    category='testing',
                    title=f"Add Molecule tests for '{role}' role",
                    description=f"The '{role}' role doesn't have Molecule tests. "
                                f"Molecule provides a standardized way to test Ansible roles across different platforms.",
                    file_paths=[os.path.join(ROLES_DIR, role)],
                    priority='medium'
                )
    
    def analyze_security(self):
        """Check for security best practices."""
        # Check for sensitive information in files
        sensitive_patterns = [
            r'password\s*:\s*["\'](?!\{\{)[^"\']',  # Hardcoded passwords
            r'secret\s*:\s*["\'](?!\{\{)[^"\']',    # Hardcoded secrets
            r'token\s*:\s*["\'](?!\{\{)[^"\']',     # Hardcoded tokens
            r'key\s*:\s*["\'](?!\{\{)[^"\']'        # Hardcoded keys
        ]
        
        for role in self.roles:
            role_path = os.path.join(ROLES_DIR, role)
            for root, _, files in os.walk(role_path):
                for file in files:
                    if file.endswith(('.yml', '.yaml', '.j2')):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            try:
                                content = f.read()
                                for pattern in sensitive_patterns:
                                    if re.search(pattern, content, re.IGNORECASE):
                                        rel_path = os.path.relpath(file_path, REPO_ROOT)
                                        self.add_suggestion(
                                            category='security',
                                            title=f"Potential sensitive information in '{rel_path}'",
                                            description=f"Found potential hardcoded sensitive information in '{rel_path}'. "
                                                        f"Consider using Ansible Vault or environment variables.",
                                            file_paths=[file_path],
                                            priority='critical'
                                        )
                                        break
                            except UnicodeDecodeError:
                                # Skip binary files
                                pass
    
    def analyze_dependencies(self):
        """Check for outdated dependencies and version pinning."""
        # Check for version pinning in requirements
        for role in self.roles:
            meta_path = os.path.join(ROLES_DIR, role, 'meta', 'main.yml')
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    try:
                        content = f.read()
                        # Check if dependencies are specified without version
                        if 'dependencies:' in content and not re.search(r'version:\s*["\'][^"\']', content):
                            self.add_suggestion(
                                category='maintenance',
                                title=f"Pin dependency versions in '{role}' role",
                                description=f"The '{role}' role has dependencies without version pinning. "
                                            f"Consider specifying versions to ensure compatibility.",
                                file_paths=[meta_path],
                                priority='medium'
                            )
                    except UnicodeDecodeError:
                        pass
        
        # Check for outdated URLs or references
        url_pattern = r'https?://[^\s"\')]+'
        for role in self.roles:
            role_path = os.path.join(ROLES_DIR, role)
            for root, _, files in os.walk(role_path):
                for file in files:
                    if file.endswith(('.yml', '.yaml', '.md', '.j2')):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            try:
                                content = f.read()
                                urls = re.findall(url_pattern, content)
                                for url in urls:
                                    # Check for GitHub raw URLs that might be versioned
                                    if 'github.com' in url and '/releases/download/' in url:
                                        rel_path = os.path.relpath(file_path, REPO_ROOT)
                                        self.add_suggestion(
                                            category='maintenance',
                                            title=f"Check for newer versions in '{rel_path}'",
                                            description=f"Found GitHub release URL in '{rel_path}': {url}. "
                                                        f"Check if newer versions are available.",
                                            file_paths=[file_path],
                                            priority='low'
                                        )
                            except UnicodeDecodeError:
                                pass
    
    def add_suggestion(self, category, title, description, file_paths, priority='medium'):
        """Add a suggestion to the list."""
        suggestion = {
            'id': len(self.suggestions) + 1,
            'category': category,
            'title': title,
            'description': description,
            'file_paths': file_paths,
            'priority': priority,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        self.suggestions.append(suggestion)
    
    def generate_output(self):
        """Generate output based on the specified format."""
        if not self.suggestions:
            print("No improvement suggestions found.")
            return
        
        if self.output_format == 'console':
            self._print_console_output()
        elif self.output_format == 'json':
            self._print_json_output()
        elif self.output_format == 'markdown':
            self._print_markdown_output()
        
        if self.github_integration:
            self._create_github_issues()
    
    def _print_console_output(self):
        """Print suggestions to console in a readable format."""
        print(f"\n=== ansible-hpc Repository Analysis Results ===\n")
        print(f"Found {len(self.suggestions)} potential improvements:\n")
        
        # Group by category
        by_category = {}
        for suggestion in self.suggestions:
            category = suggestion['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(suggestion)
        
        # Print by category
        for category, items in by_category.items():
            print(f"\n== {CATEGORIES.get(category, category)} ({len(items)}) ==\n")
            
            # Sort by priority
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            items.sort(key=lambda x: priority_order.get(x['priority'], 4))
            
            for item in items:
                print(f"[{item['priority'].upper()}] {item['title']}")
                print(f"  {item['description']}")
                print(f"  Files: {', '.join([os.path.relpath(p, REPO_ROOT) for p in item['file_paths']])}")
                print()
    
    def _print_json_output(self):
        """Print suggestions as JSON."""
        output = {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_suggestions': len(self.suggestions),
            'suggestions': self.suggestions
        }
        print(json.dumps(output, indent=2))
    
    def _print_markdown_output(self):
        """Print suggestions as Markdown."""
        md_output = [f"# ansible-hpc Repository Analysis Results\n"]
        md_output.append(f"*Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        md_output.append(f"Found **{len(self.suggestions)}** potential improvements.\n")
        
        # Group by category
        by_category = {}
        for suggestion in self.suggestions:
            category = suggestion['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(suggestion)
        
        # Print by category
        for category, items in by_category.items():
            md_output.append(f"## {CATEGORIES.get(category, category)} ({len(items)})\n")
            
            # Sort by priority
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            items.sort(key=lambda x: priority_order.get(x['priority'], 4))
            
            for item in items:
                md_output.append(f"### {item['title']}\n")
                md_output.append(f"**Priority:** {item['priority'].upper()}\n")
                md_output.append(f"{item['description']}\n")
                md_output.append(f"**Files:**\n")
                for path in item['file_paths']:
                    rel_path = os.path.relpath(path, REPO_ROOT)
                    md_output.append(f"- `{rel_path}`\n")
                md_output.append("\n")
        
        print('\n'.join(md_output))
    
    def _create_github_issues(self):
        """Create GitHub issues for suggestions (if GitHub integration is enabled)."""
        print("\nGitHub integration is not yet implemented.")
        print("To create GitHub issues, you would need to:")
        print("1. Set up GitHub API authentication")
        print("2. Use the GitHub API to create issues based on suggestions")
        print("3. Track created issues to avoid duplicates")
        print("\nConsider using the GitHub CLI or PyGithub library for implementation.")

def main():
    parser = argparse.ArgumentParser(description='Analyze ansible-hpc repository and suggest improvements')
    parser.add_argument('--format', choices=['console', 'json', 'markdown'], default='console',
                        help='Output format (default: console)')
    parser.add_argument('--github', action='store_true',
                        help='Enable GitHub integration (create issues for suggestions)')
    parser.add_argument('--category', choices=list(CATEGORIES.keys()),
                        help='Only analyze a specific category')
    parser.add_argument('--role', help='Only analyze a specific role')
    parser.add_argument('--output-file', help='Write output to file instead of stdout')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = RepoAnalyzer(output_format=args.format, github_integration=args.github)
    
    # Run analysis
    analyzer.analyze()
    
    # Filter by category if specified
    if args.category:
        analyzer.suggestions = [s for s in analyzer.suggestions if s['category'] == args.category]
    
    # Filter by role if specified
    if args.role:
        analyzer.suggestions = [s for s in analyzer.suggestions 
                               if any(args.role in p for p in s['file_paths'])]
    
    # Redirect output if specified
    if args.output_file:
        with open(args.output_file, 'w') as f:
            sys.stdout = f
            analyzer.generate_output()
            sys.stdout = sys.__stdout__
    else:
        analyzer.generate_output()

if __name__ == '__main__':
    main()