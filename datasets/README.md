# PAD Datasets

## Naming Format
`{Organization}_{Project1-Project2}_{DataType}_{Quality}_{Version}`

Example for 
* Organization FHI360
* The dataset containes Cards from Projects FHI2020 and FHI2022
* The selected Cards for training are from the middle section of a customer spreadsheet
* The Cards have been through a HIL visual inspection process to select good images and 
* This dataset is version 1.0

Yields,

`FHI360_FHI2020-FHI2022_MidTrainingSet_Good_v1.0`

## Model Dataset Mapping
| Model ID | Model Name                     | Endpoint URL                                           | Dataset Name                | Training Dataset                                                                                                                                    | Test Dataset                                                                                                                                    |
|----------|--------------------------------|--------------------------------------------------------|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| 16       | 24fhiNN1classifyAPI           | https://pad.crc.nd.edu/api/v2/neural-networks/16       | FHI2020_Stratified_Sampling | [metadata_dev.csv](https://github.com/PaperAnalyticalDeviceND/pad_dataset_registry/blob/main/datasets/FHI2020_Stratified_Sampling/metadata_dev.csv) | [metadata_test.csv](https://github.com/PaperAnalyticalDeviceND/pad_dataset_registry/blob/main/datasets/FHI2020_Stratified_Sampling/metadata_test.csv) |
| 19       | 24 fhi NN1 API concentration  | https://pad.crc.nd.edu/api/v2/neural-networks/19       | FHI2020_Stratified_Sampling | [metadata_dev.csv](https://github.com/PaperAnalyticalDeviceND/pad_dataset_registry/blob/main/datasets/FHI2020_Stratified_Sampling/metadata_dev.csv) | [metadata_test.csv](https://github.com/PaperAnalyticalDeviceND/pad_dataset_registry/blob/main/datasets/FHI2020_Stratified_Sampling/metadata_test.csv) |
| 17       | 24fhiNN1concAPI               | https://pad.crc.nd.edu/api/v2/neural-networks/17       | FHI2020_Stratified_Sampling | [metadata_dev.csv](https://github.com/PaperAnalyticalDeviceND/pad_dataset_registry/blob/main/datasets/FHI2020_Stratified_Sampling/metadata_dev.csv) | [metadata_test.csv](https://github.com/PaperAnalyticalDeviceND/pad_dataset_registry/blob/main/datasets/FHI2020_Stratified_Sampling/metadata_test.csv) |
| 18       | 24fhiPLS1conc                 | https://pad.crc.nd.edu/api/v2/neural-networks/18       | FHI2020_Stratified_Sampling | [metadata_dev.csv](https://github.com/PaperAnalyticalDeviceND/pad_dataset_registry/blob/main/datasets/FHI2020_Stratified_Sampling/metadata_dev.csv) | [metadata_test.csv](https://github.com/PaperAnalyticalDeviceND/pad_dataset_registry/blob/main/datasets/FHI2020_Stratified_Sampling/metadata_test.csv) |

