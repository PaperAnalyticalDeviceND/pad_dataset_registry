# <a id='toc1_'></a>[**Dataset Pipeline**: **`FHI_2020_strat_sampling`**](#toc0_)

This notebook is for define main steps in `FHI_2020_strat_sampling` dataset pipeline.


---

**Table of contents**<a id='toc0_'></a>    
- [**Dataset Pipeline**: **`FHI_2020_strat_sampling`**](#dataset-pipeline-fhi_2020_strat_sampling)
	- [Planning (PLN)](#planning-pln)
	- [Data Exploration (EXP)](#data-exploration-exp)
	- [Data Preprocessing (PREP)](#data-preprocessing-prep)
	- [Dataset Compilation \& Partitioning (COMP)](#dataset-compilation--partitioning-comp)
	- [Reporting and Documentation (RPT)](#reporting-and-documentation-rpt)

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

- **Define project goals:** The dataset will serve for test different solutions on the PAD quantification and classification.
- **Identify data sources:** Projects FHI2020-id-11, FHI2022-id-12 and FHI360-id-13.
- **Consider constraints:** Although we will use DVC for version controlling, The dataset must be easily downloaded without any special requirements. 

## <a id='toc1_2_'></a>[Data Exploration (EXP)](#toc0_)

**Objective:** Explore and analyze the data available from each identified source to understand its structure, quality, and potential usefulness.

Data exploration can be found in the following notebooks:

- [EXP_project-FHI2020-id-11.ipynb](EXP/EXP_project-FHI2020-id-11.ipynb)
- [EXP_project-FHI2022-id-12.ipynb](EXP/EXP_project-FHI2022-id-12.ipynb)
- [EXP_project-FHI360-id-13.ipynb](EXP/EXP_project-FHI360-id-13.ipynb)
- [EXP_blanks_rachel.ipynb](EXP/EXP_blanks_rachel.ipynb)

## <a id='toc1_3_'></a>[Data Preprocessing (PREP)](#toc0_)

**Objective:** Clean and preprocess the data to ensure it is standardized, error-free, and ready for integration.


- [PREP_FHI_2020_data.ipynb](PREP/PREP_FHI_2020_data.ipynb)

## <a id='toc1_4_'></a>[Dataset Compilation & Partitioning (COMP)](#toc0_)

**Objective:** Integrate data from various sources into a cohesive dataset. Split the data into development and test sets to prepare for model training and evaluation.

- [COMP_dataset_FHI_2020_strat_sampling_with_distractors.ipynb](COMP/COMP_dataset_FHI_2020_strat_sampling_with_distractors.ipynb)

## <a id='toc1_5_'></a>[Reporting and Documentation (RPT)](#toc0_)

**Objective:** Generate comprehensive reports detailing dataset characteristics, preprocessing steps taken, and any insights gained during exploration.

- **Automate reporting:** Create templates for generating reports that summarize key dataset aspects.
- **Maintain metadata:** Store detailed metadata alongside the dataset for easy reference.
- **Ensure accessibility:** Make reports and datasets readily available to stakeholders, with clear documentation on access and use.
