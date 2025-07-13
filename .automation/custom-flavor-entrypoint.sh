#!/bin/bash

# MegaLinter Custom Flavor Builder Entrypoint
# This script processes custom flavor configurations and generates Dockerfiles

echo "MegaLinter Custom Flavor Builder"
echo "================================="

# Default values
CUSTOM_FLAVOR_FILE=""
WORKSPACE_DIR="/workspace"
OUTPUT_DIR=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --custom-flavor|--custom-flavor-config)
            CUSTOM_FLAVOR_FILE="$2"
            shift 2
            ;;
        --workspace)
            WORKSPACE_DIR="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        python)
            # Pass through to Python directly
            exec "$@"
            ;;
        -h|--help)
            echo "Usage: $0 [--custom-flavor <file>] [--workspace <dir>] [--output-dir <dir>] | python <script> [args...]"
            echo ""
            echo "Options:"
            echo "  --custom-flavor, --custom-flavor-config  Path to the custom flavor configuration file"
            echo "  --workspace                               Workspace directory (default: /workspace)"
            echo "  --output-dir                              Output directory for generated files"
            echo "  --help                                    Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --custom-flavor-config /workspace/my-flavor.yml --output-dir /workspace/output"
            echo "  $0 python -c 'print(\"Hello from Python\")'"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            echo "Usage: $0 [--custom-flavor <file>] [--workspace <dir>] [--output-dir <dir>] | python <script> [args...]"
            exit 1
            ;;
    esac
done

# Set working directory
cd "$WORKSPACE_DIR" || exit 1

# Validate custom flavor file
if [[ -z "$CUSTOM_FLAVOR_FILE" ]]; then
    # Look for default config file
    if [[ -f "megalinter-custom-flavor.yml" ]]; then
        CUSTOM_FLAVOR_FILE="megalinter-custom-flavor.yml"
        echo "Using default configuration file: $CUSTOM_FLAVOR_FILE"
    else
        echo "Error: No custom flavor configuration file specified and megalinter-custom-flavor.yml not found"
        echo "Use --custom-flavor-config to specify the configuration file"
        exit 1
    fi
fi

if [[ ! -f "$CUSTOM_FLAVOR_FILE" ]]; then
    echo "Error: Custom flavor configuration file not found: $CUSTOM_FLAVOR_FILE"
    exit 1
fi

# Set default output directory if not specified
if [[ -z "$OUTPUT_DIR" ]]; then
    OUTPUT_DIR="$(dirname "$CUSTOM_FLAVOR_FILE")"
    if [[ "$OUTPUT_DIR" == "." ]]; then
        OUTPUT_DIR="$WORKSPACE_DIR"
    fi
fi

echo "Configuration file: $CUSTOM_FLAVOR_FILE"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Run the MegaLinter build system to generate custom flavor
cd /megalinter-src || exit 1
export PYTHONPATH="/megalinter-src:$PYTHONPATH"

python /usr/local/bin/megalinter-build.py --custom-flavor-config "$CUSTOM_FLAVOR_FILE" --output-dir "$OUTPUT_DIR"

echo ""
echo "Custom flavor generation completed"
