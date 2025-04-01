# PAD Dataset Registry Website

This directory contains the GitHub Pages website for the Paper Analytical Device (PAD) Dataset Registry. The website provides a user-friendly interface to browse and access the datasets in the repository, along with a Croissant-compliant API.

## Overview

The PAD Dataset Registry website serves as:

1. A public-facing interface for dataset discovery and access
2. A Croissant-compliant API for programmatic access to datasets
3. Documentation for the PAD datasets and how to use them

## Directory Structure

- **_data/**: Contains the dataset catalog JSON file
- **_layouts/**: Contains the layout templates for the website
- **_scripts/**: Contains Python scripts for generating metadata and catalogs
- **api/**: Contains the API endpoints and Croissant JSONLD files
- **assets/**: Contains CSS and JavaScript files for the website
- **datasets/**: Contains the individual dataset pages

## Key Scripts

The website generation relies on two main Python scripts:

### 1. validate_croissant.py

This script validates all Croissant JSONLD files in the repository to ensure they comply with the Croissant specification. It checks for:
- Required fields and properties
- Valid JSON-LD syntax
- Proper schema references
- Consistency in dataset descriptions

Usage:
```bash
python docs/_scripts/validate_croissant.py
```

### 2. generate_catalog.py

This script generates the dataset catalog that powers the website. It:
- Scans all dataset directories in the repository
- Extracts metadata from the croissant.jsonld files
- Creates a catalog.json file in the _data directory
- Generates individual dataset pages in the datasets directory
- Copies the croissant.jsonld files to the API directory

Usage:
```bash
python docs/_scripts/generate_catalog.py
```

## Automated Deployment

The website is automatically built and deployed using GitHub Actions whenever changes are pushed to the main branch. The workflow:

1. Validates all Croissant JSONLD files using validate_croissant.py
2. Generates the dataset catalog using generate_catalog.py
3. Builds the website
4. Deploys to GitHub Pages

## Additional Scripts

The _scripts directory contains additional utilities:

- **create_croissant.py**: Generates a Croissant JSONLD file for a new dataset
- **template_croissant.jsonld**: Template file used by create_croissant.py
- **requirements.txt**: Python dependencies required by the scripts

## Contributing

For information on contributing to the PAD Dataset Registry, including adding new datasets, please see the main [README.md](../README.md) file.
