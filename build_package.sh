#!/bin/bash

# Exit script on error
set -e

# Clean up the dist directory
echo "Cleaning up old builds..."
rm -rf dist/

# Build the package
echo "Building the package..."
python -m build

echo "Build completed successfully!"