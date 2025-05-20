#!/bin/bash

# Script to analyze the repository and implement improvements using GitHub Copilot
# This demonstrates how to use the repository analyzer with Copilot integration

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")" 
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
ROLE=""
CATEGORY=""
OUTPUT_DIR="$REPO_ROOT/copilot_improvements"
DRY_RUN=false

# Display help message
show_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -r, --role ROLE           Only analyze a specific role"
    echo "  -c, --category CATEGORY   Only analyze a specific category"
    echo "  -o, --output-dir DIR      Directory to save improvements (default: ./copilot_improvements)"
    echo "  -d, --dry-run             Only generate prompts, do not call Copilot"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                        # Run with default options"
    echo "  $0 -r slurm_web           # Only analyze slurm_web role"
    echo "  $0 -c documentation       # Only analyze documentation"
    echo "  $0 -d                     # Run in dry-run mode"
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--role)
            ROLE="$2"
            shift 2
            ;;
        -c|--category)
            CATEGORY="$2"
            shift 2
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Build the command
COMMAND="python3 \"$SCRIPT_DIR/copilot_integration.py\""

if [ -n "$ROLE" ]; then
    COMMAND="$COMMAND --role \"$ROLE\""
fi

if [ -n "$CATEGORY" ]; then
    COMMAND="$COMMAND --category \"$CATEGORY\""
fi

COMMAND="$COMMAND --output-dir \"$OUTPUT_DIR\""

if [ "$DRY_RUN" = true ]; then
    COMMAND="$COMMAND --dry-run"
fi

echo "Analyzing repository and generating improvements with GitHub Copilot..."
echo "This will analyze the repository and use GitHub Copilot to implement improvements."
echo ""

# Run the command
eval "$COMMAND"

echo ""
echo "Analysis and improvement generation complete!"
echo "Improvements saved to: $OUTPUT_DIR"
echo ""
echo "To view the improvements, use: ls -la $OUTPUT_DIR"