# PAD Dataset Registry

A repository of Paper Analytical Device (PAD) datasets for machine learning models, formatted according to the [MLCommons Croissant specification](http://mlcommons.org/croissant/).

## About Paper Analytical Devices

Paper Analytical Devices (PADs) are test cards that can quickly determine whether a drug tablet contains the correct medicines. They are cheap and easy to use, requiring no power, chemicals, solvents, or expensive instruments.

PADs work by performing twelve chemical tests on a drug sample and producing a distinctive color barcode that is analyzed to identify the chemical composition of the drug. If a falsified version of the medicine lacks the active ingredient or includes substitute fillers, the difference in color is perceivable by a trained human evaluator or machine learning model.

## Repository Structure

- **datasets/**: Contains the dataset directories, each with:
  - `croissant.jsonld`: The Croissant metadata file
  - `metadata_dev.csv`: The training dataset metadata
  - `metadata_test.csv`: The test dataset metadata
  - `metadata_val.csv`: The validation dataset metadata (optional)
  - `labels.csv`: The dataset labels (optional)
  - `projects.csv`: The project metadata (optional)

- **docs/**: Contains the GitHub Pages website for browsing and accessing the datasets
  - `_layouts/`: Jekyll layout templates
  - `assets/`: CSS, JS, and images
  - `_data/`: Data files for Jekyll
  - `api/`: API endpoints for Croissant-compliant data access
  - `datasets/`: Dataset pages for browsing

## Dataset Server

This repository includes a GitHub Pages website that serves as a dataset server. The server provides:

1. **Dataset Catalog**: A browsable catalog of all available datasets
2. **Dataset Pages**: Detailed information about each dataset
3. **Croissant API**: APIs for programmatically accessing the datasets
4. **Documentation**: Information about the datasets and how to use them

The server is automatically updated when changes are made to the repository through GitHub Actions.

### API Endpoints

The following API endpoints are available:

- `/api/catalog.json`: A catalog of all available datasets
- `/api/datasets/{dataset-name}.json`: The Croissant metadata for a specific dataset

## Getting Started

### Using the Datasets

To use a dataset in a machine learning project, you can access it through the catalog API:

```python
import requests
import pandas as pd

# Get the catalog
catalog = requests.get('https://paperanalyticaldevicend.github.io/pad_dataset_registry/api/catalog.json').json()

# Get metadata for a specific dataset
dataset_name = 'FHI2020_Stratified_Sampling'
dataset_info = requests.get(f'https://paperanalyticaldevicend.github.io/pad_dataset_registry/api/datasets/{dataset_name}.json').json()

# Download training data
train_data_url = next(item['contentUrl'] for item in dataset_info['distribution'] if item['name'] == 'metadata_dev.csv')
train_df = pd.read_csv(train_data_url)

# Download test data
test_data_url = next(item['contentUrl'] for item in dataset_info['distribution'] if item['name'] == 'metadata_test.csv')
test_df = pd.read_csv(test_data_url)
```

### Contributing a New Dataset

To add a new dataset to the registry:

1. Create a new directory in the `datasets` folder with your dataset name
2. Add the required files to the directory:
   - `metadata_dev.csv`: The training dataset metadata
   - `metadata_test.csv`: The test dataset metadata
   - To generate the Croissant metadata file, 
     ```bash
     cd _scripts
     python create_croissant.py --dataset-dir ../../datasets/YourDatasetName
     ```
   - Optionally you can add a README.md file which will get rendered as a webpage under **Documentation**

3. Push your changes to the repository. GitHub Actions will automatically:
   - Validate your Croissant metadata
   - Generate the dataset catalog
   - Build and deploy the website

## License

This repository and the datasets within it are licensed under the [Apache License 2.0](LICENSE).

