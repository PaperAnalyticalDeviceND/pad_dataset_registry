#!/usr/bin/env python3
"""
Generate a catalog of all datasets in the repository.
This script scans the datasets directory, reads the croissant.jsonld files,
and produces a catalog file for the website.
"""

def fix_image_paths(readme_path, dataset_name):
    """Modify image paths in README.md to use local files instead of GitHub URLs."""
    if not os.path.exists(readme_path):
        return
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Replace GitHub raw content URLs with local paths
    # Pattern for GitHub raw content: https://github.com/PaperAnalyticalDeviceND/pad_dataset_registry/raw/main/datasets/DATASET/...
    github_pattern = re.compile(r'https://github\.com/PaperAnalyticalDeviceND/pad_dataset_registry/raw/main/datasets/' + dataset_name + r'/([^\)"]+)')
    # Replace with local path
    content = github_pattern.sub(r'\1', content)
    
    with open(readme_path, 'w') as f:
        f.write(content)

import json
import os
import glob
import shutil
from datetime import datetime
import hashlib
import re

# Base paths
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
DATASETS_DIR = os.path.join(REPO_ROOT, 'datasets')
OUTPUT_DIR = os.path.join(REPO_ROOT, 'docs', '_data')
API_DIR = os.path.join(REPO_ROOT, 'docs', 'api')
DATASETS_API_DIR = os.path.join(API_DIR, 'datasets')

# Site paths
BASEURL = "/pad_dataset_registry"  # Set this to match _config.yml baseurl

# Ensure output directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(API_DIR, exist_ok=True)
os.makedirs(DATASETS_API_DIR, exist_ok=True)

# Output paths
CATALOG_FILE = os.path.join(OUTPUT_DIR, 'catalog.json')
API_CATALOG_FILE = os.path.join(API_DIR, 'catalog.json')

def get_file_size(file_path):
    """Get file size in bytes."""
    if os.path.exists(file_path):
        return os.path.getsize(file_path)
    return 0

def get_file_hash(file_path):
    """Get SHA256 hash of file."""
    if not os.path.exists(file_path):
        return None
    
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_dataset_metadata(dataset_dir):
    """Extract metadata from a dataset directory."""
    dataset_name = os.path.basename(dataset_dir)
    croissant_path = os.path.join(dataset_dir, 'croissant.jsonld')
    readme_path = os.path.join(dataset_dir, 'README.md')
    has_readme = os.path.exists(readme_path)
    
    # Skip if no croissant.jsonld file
    if not os.path.exists(croissant_path):
        return None
    
    try:
        with open(croissant_path, 'r') as f:
            croissant_data = json.load(f)
        
        # Check for required fields
        if not all(key in croissant_data for key in ['name', 'description']):
            print(f"Warning: Missing required fields in {croissant_path}")
            return None
        
        # Use existing metadata if present, otherwise build it
        metadata = {
            'name': dataset_name,
            'description': croissant_data.get('description', f'Dataset: {dataset_name}'),
            'recordCount': croissant_data.get('recordCount', 0),
            'fileCount': croissant_data.get('fileCount', 0),
            'version': croissant_data.get('version', ''),
            'datePublished': croissant_data.get('datePublished', datetime.now().isoformat()),
            'distribution': croissant_data.get('distribution', []),
            'datasetSchema': croissant_data.get('datasetSchema', None),
            'dataSplits': croissant_data.get('dataSplits', []),
            # Important: Include the baseurl in the URLs
            'url': f"{BASEURL}/datasets/{dataset_name}",
            'apiUrl': f"{BASEURL}/api/datasets/{dataset_name}.json",
            'has_readme': has_readme,
            'readme_url': f"{BASEURL}/datasets/{dataset_name}/readme" if has_readme else None
        }
        
        # Copy the Croissant file to the API directory
        api_croissant_path = os.path.join(DATASETS_API_DIR, f"{dataset_name}.json")
        with open(api_croissant_path, 'w') as out_file:
            json.dump(croissant_data, out_file, indent=2)
        
        return metadata
    
    except Exception as e:
        print(f"Error processing {croissant_path}: {str(e)}")
        return None

def main():
    """Main function to generate the catalog."""
    catalog = []
    
    # Find all dataset directories
    dataset_dirs = [d for d in glob.glob(os.path.join(DATASETS_DIR, '*')) 
                    if os.path.isdir(d) and not os.path.basename(d).startswith('.')]
    
    for dataset_dir in dataset_dirs:
        metadata = get_dataset_metadata(dataset_dir)
        if metadata:
            catalog.append(metadata)
    
    # Sort by name
    catalog.sort(key=lambda x: x['name'])
    
    # Save catalog to _data directory for Jekyll
    with open(CATALOG_FILE, 'w') as f:
        json.dump(catalog, f, indent=2)
    
    # Save catalog to API directory
    with open(API_CATALOG_FILE, 'w') as f:
        json.dump(catalog, f, indent=2)
    
    print(f"Generated catalog with {len(catalog)} datasets")
    
    # Create individual dataset pages
    for dataset in catalog:
        dataset_name = dataset['name']
        dataset_output_dir = os.path.join(REPO_ROOT, 'docs', 'datasets', dataset_name)
        os.makedirs(dataset_output_dir, exist_ok=True)
        
        # Create main dataset page
        page_content = f"""---
layout: dataset
title: {dataset_name}
dataset: {dataset_name}
---
"""
        with open(os.path.join(dataset_output_dir, 'index.md'), 'w') as f:
            f.write(page_content)
        
        # Create README page if available
        readme_source = os.path.join(DATASETS_DIR, dataset_name, 'README.md')
        if os.path.exists(readme_source):
            # Create readme directory
            readme_dir = os.path.join(dataset_output_dir, 'readme')
            os.makedirs(readme_dir, exist_ok=True)
            
            # Copy README.md to the readme directory for processing by Jekyll
            readme_dest = os.path.join(readme_dir, 'README.md')
            shutil.copy2(readme_source, readme_dest)
            
            # Fix image paths in the README.md to use local paths
            fix_image_paths(readme_dest, dataset_name)
            
            # Copy figure/image directories if they exist
            figs_source_dir = os.path.join(DATASETS_DIR, dataset_name, 'figs')
            if os.path.exists(figs_source_dir):
                figs_dest_dir = os.path.join(readme_dir, 'figs')
                if os.path.exists(figs_dest_dir):
                    shutil.rmtree(figs_dest_dir)
                shutil.copytree(figs_source_dir, figs_dest_dir)
                
            # Also copy any other image directories that might be referenced
            images_source_dir = os.path.join(DATASETS_DIR, dataset_name, 'images')
            if os.path.exists(images_source_dir):
                images_dest_dir = os.path.join(readme_dir, 'images')
                if os.path.exists(images_dest_dir):
                    shutil.rmtree(images_dest_dir)
                shutil.copytree(images_source_dir, images_dest_dir)
                
            # Copy any image files in the same directory as README.md
            dataset_dir = os.path.join(DATASETS_DIR, dataset_name)
            for file in os.listdir(dataset_dir):
                file_path = os.path.join(dataset_dir, file)
                if os.path.isfile(file_path) and file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                    shutil.copy2(file_path, os.path.join(readme_dir, file))
            
            # Create README page with special layout
            # Create front matter with f-string for variables
            front_matter = f"""---
layout: readme
title: {dataset_name} - Documentation
dataset: {dataset_name}
---
"""
            # Add the Jekyll include statement separately (not inside the f-string)
            include_statement = "{% include_relative README.md %}"
            readme_page = front_matter + include_statement
            with open(os.path.join(readme_dir, 'index.md'), 'w') as f:
                f.write(readme_page)
        
        print(f"Generated page for {dataset_name}")

if __name__ == "__main__":
    main()
