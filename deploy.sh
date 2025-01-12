#!/bin/bash

# Load environment variables from .env
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please create one with your PyPI API token."
    exit 1
fi

# Export variables from .env file
export $(grep -v '^#' .env | xargs)

# Variables
DIST_DIR="dist"
PYPI_REPO=${PYPI_REPO:-"https://upload.pypi.org/legacy/"} # Default to PyPI URL if not specified in .env
PYPI_USERNAME=${PYPI_USERNAME:-"__token__"} # Default to __token__ for API token-based auth
PYPI_PASSWORD=${PYPI_PASSWORD}

# Check for API token in environment variables
if [ -z "$PYPI_PASSWORD" ]; then
    echo "Error: PYPI_PASSWORD is not set in the .env file."
    exit 1
fi

# Check if the dist directory exists
if [ ! -d "$DIST_DIR" ]; then
    echo "Error: No build found in the $DIST_DIR directory. Run 'python -m build' first."
    exit 1
fi

# Confirm deployment
read -p "Are you sure you want to upload to PyPI? (yes/no): " CONFIRM
if [[ "$CONFIRM" != "yes" ]]; then
    echo "Aborting deployment."
    exit 1
fi

# Upload to PyPI
echo "Uploading to PyPI..."
twine upload "$DIST_DIR"/* -u "$PYPI_USERNAME" -p "$PYPI_PASSWORD" --repository-url "$PYPI_REPO"

# Check the result
if [ $? -eq 0 ]; then
    echo "Deployment to PyPI was successful!"
else
    echo "Deployment to PyPI failed."
    exit 1
fi