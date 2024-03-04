# PAD Dataset Registry

Welcome to the PAD Dataset Registry! This repository is a curated collection of datasets employed in PAD (Paper Analytical Device) projects.\
Here, we organize and store dataset metadata, which facilitates the use and management of datasets across various PAD initiatives.

Please note that actual dataset images are not stored on GitHub. We use [Data Version Control (DVC)](https://dvc.org/doc/use-cases/data-registry) to handle large datasets, which allows for efficient downloading of images directly via DVC commands.

In case you don't have access to a computer that you can install DVC on, you can still access the datasets through scripts that utilize the metadata available for the *Google Colab platform*.\
For more information on how to access the datasets using Google Colab, please refer to the [Google Colab Instructions](gcolab_instructions/README.md).


## Accessing Datasets
Requirements: dvc, dvc-gdrive and Git installed on your computer.

If you are using python, here is an example of how to set up a environment then install `dvc` and `dvc-gdrive`.
In your terminal, run the following commands:

```bash
# Create a virtual environment in the directory you want to download the datasets
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install dvc and dvc-gdrive
pip install dvc dvc-gdrive

```

### List Available Datasets 

To see the list of datasets available in the registry, you have two options:

- Examine the `datasets` directory in this repository.
- Use the DVC command to list the datasets:

    ```bash
    dvc list https://github.com/PaperAnalyticalDeviceND/pad_dataset_registry datasets
    ```

### Download Datasets 

You can download datasets from the registry using the DVC command. For example, to download the `FHI2020_Stratified_Sampling` dataset, use the following command:

```bash
dvc get https://github.com/PaperAnalyticalDeviceND/pad_dataset_registry datasets/FHI2020_Stratified_Sampling
```

This command will download all the dataset images and metadata to your local machine.
For getting a specific file, for example `metadata_dev.csv`, you can use the following command:

```bash
 dvc get https://github.com/PaperAnalyticalDeviceND/pad_dataset_registry datasets/FHI2020_Stratified_Sampling/metadata_dev.csv
```

## Dataset Structure

In the registry, each dataset is contained within its own directory and includes specific metadata and DVC files:

- `metadata_dev.csv` - Metadata for the development dataset.
- `metadata_test.csv` - Metadata for the test dataset.
- `reports/` - A directory containing reports related to the dataset.
- `dev_images.dvc` - A DVC file that links to the development images in remote storage.
- `test_images.dvc` - A DVC file that links to the test images in remote storage.

These files ensure that datasets are well-documented and that image retrieval is straightforward for researchers and contributors working on PAD projects.

Thank you for contributing to or using the PAD Dataset Registry. We are committed to supporting your research and development efforts in the field of PAD.