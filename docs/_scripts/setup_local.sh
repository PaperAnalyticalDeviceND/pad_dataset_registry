#!/bin/bash
# Setup script for local development environment

# Create necessary directories
mkdir -p ../_data
mkdir -p ../api/datasets

# Install dependencies
pip install jsonschema requests

# Generate the catalog
python generate_catalog.py

# Run validation
python validate_croissant.py

# Instructions for Jekyll
echo "To run the Jekyll site locally, execute the following commands:"
echo "cd docs"
echo "bundle install"
echo "bundle exec jekyll serve"
