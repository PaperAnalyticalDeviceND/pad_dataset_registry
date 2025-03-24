---
layout: default
title: Dataset Catalog
---

# Dataset Catalog

Browse all available PAD datasets. Each dataset is available in Croissant-compliant format with metadata and split definitions.

<table class="dataset-table">
  <thead>
    <tr>
      <th>Dataset Name</th>
      <th>Description</th>
      <th>Records</th>
      <th>Files</th>
      <th>Version</th>
      <th>Published</th>
    </tr>
  </thead>
  <tbody>
  {% for dataset in site.data.catalog %}
    <tr>
      <td><a href="{{ site.baseurl }}/datasets/{{ dataset.name }}">{{ dataset.name }}</a></td>
      <td>{{ dataset.description }}</td>
      <td>{{ dataset.recordCount }}</td>
      <td>{{ dataset.fileCount }}</td>
      <td>{{ dataset.version }}</td>
      <td>{{ dataset.datePublished | date: "%Y-%m-%d" }}</td>
    </tr>
  {% endfor %}
  </tbody>
</table>

## How to Access Datasets

All datasets are available through our GitHub repository and through our Croissant-compliant API.

### GitHub Repository

You can directly access the dataset files in our [GitHub repository]({{ site.github.repository_url }}/tree/main/datasets).

### API Access

All datasets are available through a Croissant-compliant API at:

`{{ site.url }}{{ site.baseurl }}/api/datasets/{dataset-name}.json`

A catalog of all available datasets can be accessed at:

`{{ site.url }}{{ site.baseurl }}/api/catalog.json`

### Using Datasets in Machine Learning

The datasets in this registry are designed to be used with machine learning frameworks such as TensorFlow, PyTorch, and scikit-learn. 

Each dataset includes:

1. Processed PAD card images
2. Metadata about the samples (drug name, concentration, etc.)
3. Labels for training and evaluation
4. Data splits for training, validation, and testing

To use these datasets, you can either:

1. Download the raw CSV files and process them yourself
2. Use our Croissant-compliant API to access the data programmatically
