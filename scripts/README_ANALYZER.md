# Repository Analyzer for ansible-hpc

This tool scans the ansible-hpc repository structure, identifies potential improvements, and generates suggestions that can be submitted as GitHub issues or branches.

## Purpose

The Repository Analyzer helps maintain high code quality and consistency by automatically identifying:

- Missing or incomplete documentation
- Deviations from Ansible best practices
- Incomplete role structures
- Missing tests
- Security concerns
- Outdated dependencies
- Maintenance issues

## Features

- **Multi-category analysis**: Examines documentation, best practices, role structure, testing, security, and more
- **Flexible output formats**: Console, JSON, or Markdown
- **Prioritized suggestions**: Critical, high, medium, and low priority items
- **Filtering options**: Focus on specific roles or categories
- **GitHub integration**: Future support for creating issues directly from findings

## Usage

```bash
# Basic usage (console output)
python scripts/repo_analyzer.py

# Generate markdown report
python scripts/repo_analyzer.py --format markdown

# Focus on a specific category
python scripts/repo_analyzer.py --category documentation

# Analyze a specific role
python scripts/repo_analyzer.py --role slurm_web

# Save output to a file
python scripts/repo_analyzer.py --format markdown --output-file analysis_report.md
```

## Analysis Categories

1. **Documentation** - Checks for README files, missing sections, and documentation completeness
2. **Best Practices** - Identifies hardcoded values, missing tags, and other Ansible best practice violations
3. **Role Completeness** - Verifies that roles follow the standard Ansible directory structure
4. **Testing** - Checks for test coverage and testing best practices
5. **Security** - Identifies potential security issues like hardcoded credentials
6. **Maintenance** - Finds outdated dependencies and version pinning issues

## Integration with Development Workflow

This tool can be integrated into your development workflow in several ways:

1. **Pre-commit hook**: Run analysis before committing changes
2. **CI/CD pipeline**: Include in GitHub Actions workflow to analyze PRs
3. **Scheduled runs**: Set up periodic analysis to track technical debt
4. **Manual review**: Run before releases to ensure quality standards

## Future Enhancements

- GitHub issue creation from findings
- Automatic fix suggestions with code examples
- Integration with Ansible Lint for deeper analysis
- Custom rule definitions
- Historical trend analysis

## Contributing

Contributions to improve the analyzer are welcome! Add new analysis rules, improve existing ones, or enhance the output formats.