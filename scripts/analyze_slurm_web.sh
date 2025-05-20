#!/bin/bash

# Example script to analyze the slurm_web role
# This demonstrates how to use the repository analyzer for a specific role

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Analyzing slurm_web role..."
echo "This will generate a markdown report with improvement suggestions."
echo ""

# Run the analyzer focusing on the slurm_web role
python3 "$SCRIPT_DIR/repo_analyzer.py" \
  --format markdown \
  --role slurm_web \
  --output-file "$REPO_ROOT/slurm_web_analysis.md"

echo ""
echo "Analysis complete! Report saved to: $REPO_ROOT/slurm_web_analysis.md"
echo "To view the report, use: cat $REPO_ROOT/slurm_web_analysis.md"
echo ""
echo "To analyze other roles or the entire repository, use:"
echo "  $SCRIPT_DIR/run_analyzer.sh --help"