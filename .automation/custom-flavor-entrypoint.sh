#!/bin/bash

# MegaLinter Custom Flavor Builder Entrypoint
# This script handles the custom flavor generation process

set -e

echo "MegaLinter Custom Flavor Builder"
echo "================================="

# Default values
CUSTOM_FLAVOR_FILE="/workspace/megalinter-custom-flavor.yml"
WORKSPACE_DIR="/workspace"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --custom-flavor)
      CUSTOM_FLAVOR_FILE="$2"
      shift 2
      ;;
    --workspace)
      WORKSPACE_DIR="$2"
      shift 2
      ;;
    python)
      # Allow direct python execution
      shift
      exec python "$@"
      ;;
    *)
      echo "Unknown option $1"
      echo "Usage: $0 [--custom-flavor <file>] [--workspace <dir>] | python <script> [args...]"
      exit 1
      ;;
  esac
done

# Change to workspace directory if it exists
if [ -d "$WORKSPACE_DIR" ]; then
  cd "$WORKSPACE_DIR"
  echo "Working directory: $WORKSPACE_DIR"
fi

# Check if custom flavor file exists
if [ ! -f "$CUSTOM_FLAVOR_FILE" ]; then
  echo "Error: Custom flavor file not found: $CUSTOM_FLAVOR_FILE"
  exit 1
fi

echo "Using custom flavor configuration: $CUSTOM_FLAVOR_FILE"

# Run the custom flavor generation
echo "Generating custom flavor Dockerfile..."
cd /megalinter
python /automation/build.py --custom-flavor "$CUSTOM_FLAVOR_FILE"

echo "Custom flavor generation completed successfully!"

# Copy generated Dockerfile to workspace
if [ -f "/megalinter/Dockerfile-custom-flavor" ] && [ "$WORKSPACE_DIR" != "/megalinter" ]; then
  cp /megalinter/Dockerfile-custom-flavor "$WORKSPACE_DIR/"
  echo "Dockerfile-custom-flavor copied to $WORKSPACE_DIR"
fi
