# <a id='toc1_'></a>[**Dataset Pipeline**: **`MSH-Tanzania`**](#toc0_)


**Table of contents**<a id='toc0_'></a>    
- [**Dataset Pipeline**: **`MSH-Tanzania`**](#toc1_)    
  - [Planning (PLN)](#toc1_1_)    
  - [Data Exploration (EXP)](#toc1_2_)    
  - [Data Preprocessing (PREP)](#toc1_3_)    
  - [Dataset Compilation & Partitioning (COMP)](#toc1_4_)    
  - [Reporting and Documentation (RPT)](#toc1_5_)    

<!-- vscode-jupyter-toc-config
	numbering=false
	anchor=true
	flat=false
	minLevel=1
	maxLevel=6
	/vscode-jupyter-toc-config -->
<!-- THIS CELL WILL BE REPLACED ON TOC UPDATE. DO NOT WRITE YOUR TEXT IN THIS CELL -->

---

## <a id='toc1_1_'></a>[Planning (PLN)](#toc0_)

**Objective:** Define the purpose, scope, and objectives of the dataset. Identify potential data sources and outline the methodology to be used throughout the pipeline.

- **Define project goals:** 
  - The dataset will serve for test different solutions on the PAD classification.
- **Identify data sources:** 
  - In the API the Project id is 19.
  - The file [MSH-Tanzania-PAD-Summary-of-reads-by-TFDA-and-SB.xlsx](data/raw/MSH-Tanzania-PAD-Summary-of-reads-by-TFDA-and-SB.xlsx) has the information about the samples to be used in the dataset.
  - The table `double_blind` in [phpmyadmin](https://pad.crc.nd.edu/phpmyadmin/).
  - Other important files are in [PAD-MSH-Tanzania](https://drive.google.com/drive/u/0/folders/0ACcr4dCeZ_cWUk9PVA).
- **Consider constraints:** 
  - no constraints until now.

## <a id='toc1_2_'></a>[Data Exploration (EXP)](#toc0_)

**Objective:** Explore and analyze the data available from each identified source to understand its structure, quality, and potential usefulness.

**We explored data from three data sources** 
  - Data from the PAD API for the Project id=19 (MSH-Tanzania)
  - Data from the spreadsheet [MSH-Tanzania-PAD-Summary-of-reads-by-TFDA-and-SB.xlsx](MSH-Tanzania-PAD-Summary-of-reads-by-TFDA-and-SB.xlsx)
  - The table `double_blind` in [PAD Database](https://pad.crc.nd.edu/phpmyadmin/) database

The code for data exploration is in the notebook [EXP__project-MSH-Tanzania.ipynb](EXP__project-MSH-Tanzania.ipynb).

The output of this step was saved in the file [data/processed/recovered_data.csv](data/processed/recovered_data.csv).

## <a id='toc1_3_'></a>[Data Preprocessing (PREP)](#toc0_)

**Objective:** Clean and preprocess the data to ensure it is standardized, free of errors, and ready for integration.

- The code for data preprocessing is in the notebook [PREP__project-MSH-Tanzania.ipynb](PREP__project-MSH-Tanzania.ipynb).
- The output of this step was saved in the file [data/processed/MSH-Tanzania_metadata_all.csv](data/processed/MSH-Tanzania_metadata_all.csv).


## <a id='toc1_4_'></a>[Dataset Compilation & Partitioning (COMP)](#toc0_)

**Objective:** Integrate data from various sources into a cohesive dataset. Split the data into development and test sets to prepare for model training and evaluation.

- [COMP__project-MSH-Tanzania.ipynb](COMP__project-MSH-Tanzania.ipynb)

## <a id='toc1_5_'></a>[Reporting and Documentation (RPT)](#toc0_)

**Objective:** Generate comprehensive reports detailing dataset characteristics, preprocessing steps taken, and any insights gained during exploration.

- **Automate reporting:** Create templates for generating reports that summarize key dataset aspects.
- **Maintain metadata:** Store detailed metadata alongside the dataset for easy reference.
- **Ensure accessibility:** Make reports and datasets readily available to stakeholders, with clear documentation on access and use.
