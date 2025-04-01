# PAD Dataset Registry

This directory contains the GitHub Pages website for the Paper Analytical Device (PAD) Dataset Registry. The website provides a user-friendly interface to browse and access the datasets in the repository.

## Features

- **Croissant-Compliant API**: All datasets are available through a Croissant-compliant API
- **Dataset Catalog**: A searchable catalog of all available datasets
- **Dataset Details**: Detailed information about each dataset, including metadata, files, and data splits
- **Automated Deployment**: The website is automatically built and deployed using GitHub Actions

## Getting Started

For detailed instructions on setting up and deploying the dataset server, see [SETUP.md](SETUP.md).

## Quick Start

1. **Generate a Croissant JSONLD file for a dataset**

```bash
cd _scripts
python create_croissant.py --dataset-dir ../../datasets/YourDatasetName
```

2. **Generate the dataset catalog**

```bash
python generate_catalog.py
```

3. **Test the site locally**

```bash
cd ..
bundle exec jekyll serve
```

4. **Access the site**

Open your browser to http://localhost:4000/pad_dataset_registry/

## Directory Structure

- **_data/**: Contains the dataset catalog JSON file
- **_layouts/**: Contains the Jekyll layout templates
- **_scripts/**: Contains Python scripts for generating metadata and catalogs
- **api/**: Contains the API endpoints
- **assets/**: Contains CSS and JavaScript files
- **datasets/**: Contains the dataset pages

## Contributing

If you'd like to contribute to the PAD Dataset Registry, please see the main [README.md](../README.md) file for information.
