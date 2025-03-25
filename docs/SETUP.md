# Setting Up the PAD Dataset Registry Server

This document provides detailed instructions for setting up and deploying the PAD Dataset Registry using GitHub Pages.

## Prerequisites

- A GitHub account with access to the repository
- Git installed on your machine
- Python 3.7+ installed
- Basic knowledge of command line operations

## 1. Initial Setup

### 1.1 Clone the Repository

```bash
git clone https://github.com/PaperAnalyticalDeviceND/pad_dataset_registry.git
cd pad_dataset_registry
```

### 1.2 Install Required Python Packages

```bash
pip install pandas jsonschema requests
```

### 1.3 Make Scripts Executable

```bash
chmod +x docs/_scripts/*.py
```

## 2. Generating Croissant JSONLD Files

### 2.1 Generate for an Existing Dataset

```bash
cd docs/_scripts
python create_croissant.py --dataset-dir ../../datasets/FHI2020_Stratified_Sampling
```

Follow the prompts to provide:
- A description for the dataset
- A version (e.g., v1.0)
- Your name (as the creator)

The script will:
1. Analyze the dataset directory
2. Count records in the CSV files
3. Generate a schema based on the CSV columns
4. Create a properly formatted croissant.jsonld file

### 2.2 Verify the Generated File

Check that the croissant.jsonld file was created successfully:

```bash
cat ../../datasets/FHI2020_Stratified_Sampling/croissant.jsonld
```

### 2.3 Validate the Croissant JSONLD Files

```bash
python validate_croissant.py
```

This will check all croissant.jsonld files in the repository for correctness.

## 3. Generating the Dataset Catalog

### 3.1 Run the Catalog Generator

```bash
python generate_catalog.py
```

This script will:
1. Scan all dataset directories
2. Extract metadata from the croissant.jsonld files
3. Create a catalog.json file in the docs/_data directory
4. Create dataset pages in the docs/datasets directory
5. Copy the croissant.jsonld files to the API directory

### 3.2 Verify the Generated Catalog

Check that the catalog was created successfully:

```bash
cat ../_data/catalog.json
```

## 4. Local Testing with Jekyll

### 4.1 Install Ruby and Jekyll

On macOS:
```bash
brew install ruby
gem install bundler jekyll
```

On Ubuntu:
```bash
sudo apt-get install ruby-full build-essential zlib1g-dev
gem install bundler jekyll
```

On Windows, use [RubyInstaller](https://rubyinstaller.org/).

### 4.2 Set Up Jekyll in the docs Directory

```bash
cd ../
bundle init
bundle add jekyll github-pages webrick
```

### 4.3 Run Jekyll Locally

```bash
bundle exec jekyll serve
```

Visit http://localhost:4000/pad_dataset_registry/ in your browser to see the site.

## 5. Configuring GitHub Pages

### 5.1 Enable GitHub Pages in Repository Settings

1. Go to the repository on GitHub
2. Click on "Settings" > "Pages"
3. Under "Source", select the branch you want to deploy from (main or gh-pages)
4. Set the directory to "/docs"
5. Click "Save"

### 5.2 Set Up GitHub Actions Permissions

1. Go to "Settings" > "Actions" > "General"
2. Under "Workflow permissions", select "Read and write permissions"
3. Click "Save"

### 5.3 Create GitHub Actions Workflow

The workflow file is already included in `.github/workflows/build-and-deploy.yml`. If it's missing, you can create it:

```yaml
name: Build and Deploy GitHub Pages

on:
  push:
    branches: [ main, dataset_server ]
    paths:
      - 'datasets/**'
      - 'docs/**'
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # fetch all history

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install jsonschema pyyaml requests pandas

      - name: Validate Croissant JSONLDs
        run: python docs/_scripts/validate_croissant.py
      
      - name: Generate dataset catalog
        run: python docs/_scripts/generate_catalog.py
      
      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.0'
          bundler-cache: true

      - name: Install Jekyll
        run: |
          gem install jekyll bundler
          cd docs
          bundle init
          bundle add jekyll github-pages webrick
        
      - name: Build Jekyll site
        run: |
          cd docs
          bundle exec jekyll build --trace
      
      - name: Deploy to GitHub Pages
        uses: JamesIves/github-pages-deploy-action@v4
        with:
          folder: docs/_site
          branch: gh-pages
```

## 6. Deploying to GitHub Pages

### 6.1 Commit and Push Changes

```bash
git add .
git commit -m "Implement Croissant-compliant dataset server"
git push origin dataset_server
```

### 6.2 Create a Pull Request

1. Go to the repository on GitHub
2. Click on "Pull requests" > "New pull request"
3. Select `dataset_server` as the compare branch
4. Click "Create pull request"
5. Add a description of the changes
6. Click "Create pull request"

### 6.3 Merge the Pull Request

1. Once all checks pass, click "Merge pull request"
2. Click "Confirm merge"

### 6.4 View the Deployed Site

1. Go to Settings > Pages to find the published URL
2. Visit your site at: https://PaperAnalyticalDeviceND.github.io/pad_dataset_registry/

## 7. Adding New Datasets

### 7.1 Create a New Dataset Directory

```bash
mkdir -p datasets/NewDatasetName
```

### 7.2 Add Dataset Files

1. Add the dataset files:
   - `metadata_dev.csv`: Training data
   - `metadata_test.csv`: Test data
   - `metadata_val.csv`: Validation data (optional)

### 7.3 Generate a Croissant JSONLD File

```bash
cd docs/_scripts
python create_croissant.py --dataset-dir ../../datasets/NewDatasetName
```

### 7.4 Commit and Push the New Dataset

```bash
git add datasets/NewDatasetName
git commit -m "Add NewDatasetName dataset"
git push origin main
```

The GitHub Actions workflow will automatically update the site.

## 8. Troubleshooting

### 8.1 JSON Parsing Errors

If you encounter JSON parsing errors when running the scripts:

1. Check that the JSON files are properly formatted
2. Validate the JSON files using a tool like [JSONLint](https://jsonlint.com/)
3. Make sure there are no unescaped special characters

### 8.2 GitHub Pages Build Failures

If the GitHub Pages build fails:

1. Check the Actions tab for error messages
2. Look for syntax errors in your Liquid templates
3. Verify that _config.yml is correctly formatted
4. Make sure all dependencies are installed in the workflow

### 8.3 Script Execution Issues

If the scripts fail to run:

1. Check file permissions: `chmod +x docs/_scripts/*.py`
2. Verify you have the required packages: `pip install pandas jsonschema requests`
3. Check for Python version compatibility issues

### 8.4 Local Jekyll Issues

If Jekyll fails to run locally:

1. Install the required gems: `gem install jekyll bundler webrick`
2. Check for Ruby version compatibility
3. Try clearing the Jekyll cache: `bundle exec jekyll clean`

## Need Help?

If you encounter any issues not covered in this guide, please open an issue on the GitHub repository or contact the maintainers directly.
