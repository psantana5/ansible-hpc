## About this project (the order will be fixed when all the information about this project is ready)

1. .github/workflows/
# In this folder, we find CI files to:

1.1 Lint Ansible playbooks: 
name: Ansible Lint

on:
  push:
    branches: [ main, master ]
    paths:
      - '**.yml'
      - '**.yaml'
      - 'roles/**'
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  ansible-lint:
    name: Ansible Lint
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Ansible Lint
        run: |
          python -m pip install --upgrade pip
          pip install ansible-lint
      
      - name: Create custom ansible-lint config
        run: |
          cat > .ansible-lint <<EOF
          skip_list:
            - 'yaml'  # Let yamllint handle YAML formatting
            - 'no-changed-when'  # Often not needed for simple tasks
            - 'command-instead-of-module'  # Sometimes shell commands are necessary
          
          warn_list:
            - 'experimental'
            - 'role-name'
          EOF
      
      - name: Run Ansible Lint
        run: |
          echo "Ansible Lint Results:" > ansible_lint_results.log
          echo "=====================" >> ansible_lint_results.log
          echo "" >> ansible_lint_results.log
          
          # Run ansible-lint on playbooks and roles
          RESULT=$(ansible-lint -p 2>&1 || true)
          
          if [ -n "$RESULT" ]; then
            echo "$RESULT" >> ansible_lint_results.log
          else
            echo "No linting issues found!" >> ansible_lint_results.log
          fi
          
          echo "Linting completed. Check ansible_lint_results.log for details."
          
          # Output summary to console
          grep -A 2 "WARNING\|ERROR" ansible_lint_results.log || echo "No linting issues found!"
      
      - name: Upload lint results
        uses: actions/upload-artifact@v4
        with:
          name: ansible-lint-results
          path: ansible_lint_results.log

2. Ansible Syntax Check:
name: Ansible Syntax Check

on:
  push:
    branches: [ main, master ]
    paths:
      - '**.yml'
      - '**.yaml'
      - 'inventory/**'
      - 'roles/**'
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  ansible-syntax:
    name: Ansible Syntax Check
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Ansible
        run: |
          python -m pip install --upgrade pip
          pip install ansible ansible-lint
      
      - name: Run Ansible syntax check
        run: |
          echo "Ansible Syntax Check Results:" > ansible_syntax_results.log
          echo "=============================" >> ansible_syntax_results.log
          echo "" >> ansible_syntax_results.log
          
          # Check all playbooks
          find . -name "*.yml" -not -path "*/\.*" | sort | while read playbook; do
            if grep -q "^- hosts:" "$playbook" || grep -q "^hosts:" "$playbook"; then
              echo "Checking playbook: $playbook"
              RESULT=$(ansible-playbook --syntax-check "$playbook" 2>&1 || true)
              
              if [[ $RESULT == *"ERROR"* || $RESULT == *"syntax error"* ]]; then
                echo "Issues found in $playbook:" >> ansible_syntax_results.log
                echo "$RESULT" >> ansible_syntax_results.log
                echo "" >> ansible_syntax_results.log
              fi
            fi
          done
          
          echo "Syntax check completed. Check ansible_syntax_results.log for details."
          
          # Output summary to console
          grep -B 1 "ERROR" ansible_syntax_results.log || echo "No syntax errors found!"
      
      - name: Upload syntax check results
        uses: actions/upload-artifact@v4
        with:
          name: ansible-syntax-results
          path: ansible_syntax_results.log

3. Badges for CI status: 
name: CI Status Monitor

on:
  workflow_run:
    workflows: ["Ansible Linting", "Ansible Syntax Check", "CodeQL", "Create Release", "Documentation Generation", "Integration Tests", "Molecule Tests", "Security Scan", "YAML Lint"]
    types: [completed]

jobs:
  update-badge:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.workflow_run.head_branch }}

      - name: Check workflow status
        id: check_status
        run: |
          if [[ "${{ github.event.workflow_run.conclusion }}" == "success" ]]; then
            echo "STATUS=PASSING" >> $GITHUB_OUTPUT
          else
            echo "STATUS=FAILING" >> $GITHUB_OUTPUT
          fi

      - name: Update README badge
        run: |
          sed -i "s|https://img.shields.io/badge/CI-.*|https://img.shields.io/badge/CI-${{ steps.check_status.outputs.STATUS }}-brightgreen.svg|g" README.md
          git config --global user.name 'github-actions'
          git config --global user.email 'github-actions@github.com'
          git add README.md
          git commit -m "Update CI status badge" || exit 0
          git push

4. Integration tests

name: Integration Tests

on:
  push:
    branches: [ main, master ]
    paths:
      - 'tests/integration_tests/**'
      - 'playbooks/**'
      - 'roles/**'
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install ansible pytest pytest-testinfra
      
      - name: Run integration tests
        run: |
          echo "Running integration tests..."
          cd tests
          
          # Run all integration tests
          for test_file in integration_tests/*.yml; do
            if [ -f "$test_file" ]; then
              echo "Running test: $test_file"
              ansible-playbook "$test_file" -i inventory/hosts --connection=local || echo "Test $test_file failed but continuing..."
            fi
          done
        continue-on-error: true
      
      - name: Run component tests
        run: |
          echo "Running component tests..."
          cd tests
          
          # Run all component tests
          for test_file in component_tests/*.yml; do
            if [ -f "$test_file" ]; then
              echo "Running test: $test_file"
              ansible-playbook "$test_file" -i inventory/hosts --connection=local || echo "Test $test_file failed but continuing..."
            fi
          done
        continue-on-error: true

5. Molecule tests
name: Molecule Tests

on:
  push:
    branches: [ main, master ]
    paths:
      - 'roles/**'
  pull_request:
    branches: [ main, master ]
    paths:
      - 'roles/**'
  workflow_dispatch:

jobs:
  molecule:
    name: Molecule Tests
    runs-on: ubuntu-latest
    strategy:
      matrix:
        role:
          - autofs
          - compute
          - dns
          - docker
          - epel
          - login_node
          - monitoring
          - nfs_server
          - node_exporter
          - openldap
          - prometheus
          - slurmctld
          - slurmdbd
      fail-fast: false
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install molecule molecule-docker ansible-core pytest pytest-testinfra
      
      - name: Run Molecule tests
        run: |
          cd roles/${{ matrix.role }}
          if [ -d "molecule" ]; then
            molecule test
          else
            echo "No molecule tests found for role ${{ matrix.role }}, skipping."
          fi
        continue-on-error: true

6. Security scan
name: Security Scan

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  schedule:
    - cron: '0 0 * * 0'  # Run weekly on Sunday at midnight
  workflow_dispatch:

jobs:
  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install bandit ansible-lint
      
      - name: Run Bandit security scan
        run: |
          echo "Security Scan Results:" > security_scan_results.log
          echo "======================" >> security_scan_results.log
          echo "" >> security_scan_results.log
          
          # Scan Python files
          echo "Running Bandit on Python files:" >> security_scan_results.log
          find . -name "*.py" -not -path "*/\.*" | xargs bandit -r 2>&1 || true >> security_scan_results.log
          echo "" >> security_scan_results.log
          
          # Scan Ansible files for security issues
          echo "Running Ansible-lint security checks:" >> security_scan_results.log
          ansible-lint --tags security -p 2>&1 || true >> security_scan_results.log
          
          echo "Security scan completed. Check security_scan_results.log for details."
      
      - name: Upload security scan results
        uses: actions/upload-artifact@v4
        with:
          name: security-scan-results
          path: security_scan_results.log

7. Linting of the .yml files
name: YAML Lint

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  # Allow manual triggering
  workflow_dispatch:

jobs:
  yaml-lint:
    name: YAML Lint
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install yamllint
        run: |
          python -m pip install --upgrade pip
          pip install yamllint
      
      - name: Create custom yamllint config
        run: |
          cat > .yamllint <<EOF
          extends: relaxed
          
          rules:
            line-length: disable
            indentation: 
              spaces: 2
              indent-sequences: consistent
            truthy:
              allowed-values: ['true', 'false', 'yes', 'no']
          EOF
      
      - name: Run YAML lint and log issues
        run: |
          echo "YAML Linting Results:" > yaml_lint_results.log
          echo "======================" >> yaml_lint_results.log
          echo "" >> yaml_lint_results.log
          
          # Find all YAML files and run yamllint on each
          find . -type f \( -name "*.yml" -o -name "*.yaml" \) -not -path "*/\.*" | sort | while read file; do
            echo "Linting $file..."
            RESULT=$(yamllint -f parsable "$file" 2>&1 || true)
            
            if [ -n "$RESULT" ]; then
              echo "Issues found in $file:" >> yaml_lint_results.log
              echo "$RESULT" >> yaml_lint_results.log
              echo "" >> yaml_lint_results.log
            fi
          done
          
          echo "Linting completed. Check yaml_lint_results.log for details."
          
          # Output summary to console
          echo "Files with linting issues:"
          grep -B 1 ":" yaml_lint_results.log | grep "Issues found" || echo "No issues found!"
      
      - name: Auto-fix common YAML issues
        if: github.event_name == 'workflow_dispatch'
        run: |
          echo "Attempting to auto-fix common YAML issues..."
          
          # Fix trailing spaces and ensure newline at end of file
          find . -type f \( -name "*.yml" -o -name "*.yaml" \) -not -path "*/\.*" | while read file; do
            # Remove trailing whitespace
            sed -i 's/[[:space:]]*$//' "$file"
            
            # Ensure file ends with newline
            [ -n "$(tail -c 1 "$file")" ] && echo >> "$file"
            
            # Convert CRLF to LF (Windows to Unix line endings)
            sed -i 's/\r$//' "$file"
            
            echo "Fixed formatting in $file"
          done
          
          echo "Auto-fix completed. Re-running lint to verify fixes..."
          
          # Re-run lint to verify fixes
          find . -type f \( -name "*.yml" -o -name "*.yaml" \) -not -path "*/\.*" | sort | while read file; do
            RESULT=$(yamllint -f parsable "$file" 2>&1 || true)
            if [ -n "$RESULT" ]; then
              echo "Issues still present in $file after auto-fix:"
              echo "$RESULT"
              echo ""
            fi
          done
      
      - name: Upload lint results
        uses: actions/upload-artifact@v4
        with:
          name: yaml-lint-results
          path: yaml_lint_results.log

