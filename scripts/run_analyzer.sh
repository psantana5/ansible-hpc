#!/bin/bash

# Run Repository Analyzer for ansible-hpc
# This script provides a convenient way to run the repository analyzer

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
OUTPUT_FORMAT="markdown"
OUTPUT_FILE="$REPO_ROOT/analysis_report.md"
GITHUB_INTEGRATION="false"
CATEGORY=""
ROLE=""

# Display help message
show_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -f, --format FORMAT       Output format: console, json, markdown (default: markdown)"
    echo "  -o, --output FILE         Output file (default: analysis_report.md)"
    echo "  -g, --github              Enable GitHub integration"
    echo "  -c, --category CATEGORY   Only analyze a specific category"
    echo "  -r, --role ROLE           Only analyze a specific role"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                        # Run with default options"
    echo "  $0 -f console             # Display results in console"
    echo "  $0 -c documentation       # Only analyze documentation"
    echo "  $0 -r slurm_web           # Only analyze slurm_web role"
    echo "  $0 -g                     # Enable GitHub integration"
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -g|--github)
            GITHUB_INTEGRATION="true"
            shift
            ;;
        -c|--category)
            CATEGORY="$2"
            shift 2
            ;;
        -r|--role)
            ROLE="$2"
            shift 2
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

# Build command
CMD="python3 $SCRIPT_DIR/repo_analyzer.py --format $OUTPUT_FORMAT"

# Add options if specified
if [ "$GITHUB_INTEGRATION" = "true" ]; then
    CMD="$CMD --github"
fi

if [ -n "$CATEGORY" ]; then
    CMD="$CMD --category $CATEGORY"
fi

if [ -n "$ROLE" ]; then
    CMD="$CMD --role $ROLE"
fi

if [ "$OUTPUT_FORMAT" != "console" ]; then
    CMD="$CMD --output-file $OUTPUT_FILE"
    echo "Running analyzer and saving output to $OUTPUT_FILE"
else
    echo "Running analyzer with console output"
fi

# Run the command
eval $CMD

# Check if output file was created
if [ "$OUTPUT_FORMAT" != "console" ] && [ -f "$OUTPUT_FILE" ]; then
    echo "Analysis complete! Report saved to: $OUTPUT_FILE"
    
    # If GitHub integration is enabled, offer to create issues/branches
    if [ "$GITHUB_INTEGRATION" = "true" ] && [ "$OUTPUT_FORMAT" = "json" ]; then
        echo ""
        echo "Would you like to create GitHub issues or branches from the analysis?"
        echo "1. Create issues"
        echo "2. Create branches"
        echo "3. Skip"
        read -p "Select an option (1-3): " GITHUB_OPTION
        
        case $GITHUB_OPTION in
            1)
                python3 $SCRIPT_DIR/github_integration.py --suggestions-file "$OUTPUT_FILE" --create-issues
                ;;
            2)
                python3 $SCRIPT_DIR/github_integration.py --suggestions-file "$OUTPUT_FILE" --create-branches
                ;;
            *)
                echo "Skipping GitHub integration"
                ;;
        esac
    fi
fi