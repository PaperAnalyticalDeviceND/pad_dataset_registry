---
layout: default
title: PAD Dataset Registry
---

# Paper Analytical Device (PAD) Dataset Registry

Welcome to the PAD Dataset Registry, a collection of datasets used for training, validating, and testing machine learning models for the detection of falsified pharmaceuticals using Paper Analytical Devices.

## About Paper Analytical Devices

Paper Analytical Devices (PADs) are test cards that can quickly determine whether a drug tablet contains the correct medicines. They are cheap and easy to use, requiring no power, chemicals, solvents, or expensive instruments.

PADs work by performing twelve chemical tests on a drug sample and producing a distinctive color barcode that is analyzed to identify the chemical composition of the drug. If a falsified version of the medicine lacks the active ingredient or includes substitute fillers, the difference in color is perceivable by a trained human evaluator or machine learning model.

## Available Datasets

Our datasets are formatted according to the [MLCommons Croissant specification](http://mlcommons.org/croissant/), making them easily accessible for machine learning applications.

<div class="dataset-grid">
  {% for dataset in site.data.catalog %}
    <div class="dataset-card">
      <h3><a href="{{ site.baseurl }}/datasets/{{ dataset.name }}">{{ dataset.name }}</a></h3>
      <p>{{ dataset.description }}</p>
      <p><strong>Records:</strong> {{ dataset.recordCount }}</p>
      <a href="{{ site.baseurl }}/datasets/{{ dataset.name }}" class="button">View Details</a>
    </div>
  {% endfor %}
</div>

## How to Use

These datasets can be used to train machine learning models to detect falsified pharmaceuticals. Each dataset contains:

1. Processed PAD card images
2. Metadata about the samples (drug name, concentration, etc.)
3. Labels for training and evaluation
4. Data splits for training, validation, and testing

## API Access

All datasets are available through a Croissant-compliant API at:

`{{ site.url }}{{ site.baseurl }}/api/datasets/{dataset-name}.json`

A catalog of all available datasets can be accessed at:

`{{ site.url }}{{ site.baseurl }}/api/catalog.json`
