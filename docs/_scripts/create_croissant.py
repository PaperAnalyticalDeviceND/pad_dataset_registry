#!/usr/bin/env python3
"""
Generate a new croissant.jsonld file for a dataset.
This script prompts the user for dataset information and creates a new croissant.jsonld file.
"""

import json
import os
import datetime
import hashlib
import pandas as pd
import argparse
from pathlib import Path

def get_file_hash(file_path):
    """Get SHA256 hash of file."""
    if not os.path.exists(file_path):
        return None
    
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_file_size(file_path):
    """Get file size in bytes."""
    if os.path.exists(file_path):
        return os.path.getsize(file_path)
    return 0

def load_template():
    """Load the template croissant.jsonld file."""
    template_path = os.path.join(os.path.dirname(__file__), 'template_croissant.jsonld')
    try:
        with open(template_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing template JSON: {str(e)}")
        raise

def get_csv_schema(csv_path):
    """Get schema information from a CSV file."""
    try:
        df = pd.read_csv(csv_path, nrows=1)
        columns = []
        
        for column in df.columns:
            dtype = df[column].dtype
            
            if pd.api.types.is_integer_dtype(dtype):
                data_type = "integer"
                type_str = "xsd:integer"
            elif pd.api.types.is_float_dtype(dtype):
                data_type = "number"
                type_str = "xsd:decimal"
            elif pd.api.types.is_bool_dtype(dtype):
                data_type = "boolean"
                type_str = "xsd:boolean"
            elif pd.api.types.is_datetime64_dtype(dtype):
                data_type = "datetime"
                type_str = "xsd:dateTime"
            else:
                data_type = "string"
                type_str = "xsd:string"
            
            columns.append({
                "@type": type_str,
                "name": column,
                "description": f"Column: {column}",
                "dataType": data_type
            })
        
        return columns
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return []

def count_records(csv_path):
    """Count the number of records in a CSV file."""
    try:
        # Use pandas to count rows efficiently, even for large files
        return pd.read_csv(csv_path).shape[0]
    except Exception as e:
        print(f"Error counting records in {csv_path}: {str(e)}")
        return 0

def main():
    """Main function to generate croissant.jsonld file."""
    parser = argparse.ArgumentParser(description='Generate a croissant.jsonld file for a dataset')
    parser.add_argument('--dataset-dir', type=str, help='Path to the dataset directory')
    args = parser.parse_args()
    
    # Default to interactive mode if no directory is provided
    if args.dataset_dir:
        dataset_dir = args.dataset_dir
    else:
        # Get the dataset directory from the user
        dataset_dir = input("Enter the path to the dataset directory: ")
    
    if not os.path.exists(dataset_dir):
        print(f"Error: Directory '{dataset_dir}' does not exist.")
        return
    
    print(f"Loading template...")
    # Load the template
    try:
        template = load_template()
    except Exception as e:
        print(f"Error loading template: {str(e)}")
        return
    
    print(f"Template loaded successfully")
    
    # Get the dataset name
    dataset_name = os.path.basename(os.path.abspath(dataset_dir))
    print(f"Dataset name: {dataset_name}")
    
    # Populate the template with basic information
    template['name'] = dataset_name
    template['description'] = input(f"Enter a description for {dataset_name}: ")
    template['version'] = input("Enter a version (e.g., v1.0): ")
    template['datePublished'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    template['creator']['name'] = input("Enter your name: ")
    
    # Update the @id and url fields
    github_repo = "https://github.com/PaperAnalyticalDeviceND/pad_dataset_registry"
    template['@id'] = f"{github_repo}/tree/main/datasets/{dataset_name}"
    template['url'] = f"{github_repo}/tree/main/datasets/{dataset_name}"
    
    # Check for metadata_dev.csv and metadata_test.csv
    dev_path = os.path.join(dataset_dir, 'metadata_dev.csv')
    test_path = os.path.join(dataset_dir, 'metadata_test.csv')
    
    distribution = []
    
    # Process metadata_dev.csv if it exists
    if os.path.exists(dev_path):
        print(f"Processing training dataset: {dev_path}")
        dev_hash = get_file_hash(dev_path)
        dev_size = get_file_size(dev_path)
        dev_record_count = count_records(dev_path)
        
        dev_item = {
            "@type": [
                "cr:FileObject",
                "schema:MediaObject",
                "schema:DataDownload"
            ],
            "@id": f"datasets/{dataset_name}/metadata_dev.csv",
            "name": "metadata_dev.csv",
            "description": f"Train dataset for {dataset_name}",
            "contentUrl": f"{github_repo}/raw/main/datasets/{dataset_name}/metadata_dev.csv",
            "encodingFormat": "text/csv",
            "sha256": dev_hash,
            "dateModified": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "contentSize": f"{dev_size} bytes",
            "inLanguage": "en"
        }
        distribution.append(dev_item)
        
        # Get schema from dev file
        columns = get_csv_schema(dev_path)
        if columns:
            template['datasetSchema'] = {
                "@type": "cr:TableSchema",
                "columns": columns
            }
    else:
        print(f"Warning: metadata_dev.csv not found in {dataset_dir}")
        dev_record_count = 0
    
    # Process metadata_test.csv if it exists
    if os.path.exists(test_path):
        print(f"Processing test dataset: {test_path}")
        test_hash = get_file_hash(test_path)
        test_size = get_file_size(test_path)
        test_record_count = count_records(test_path)
        
        test_item = {
            "@type": [
                "cr:FileObject",
                "schema:MediaObject",
                "schema:DataDownload"
            ],
            "@id": f"datasets/{dataset_name}/metadata_test.csv",
            "name": "metadata_test.csv",
            "description": f"Test dataset for {dataset_name}",
            "contentUrl": f"{github_repo}/raw/main/datasets/{dataset_name}/metadata_test.csv",
            "encodingFormat": "text/csv",
            "sha256": test_hash,
            "dateModified": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "contentSize": f"{test_size} bytes",
            "inLanguage": "en"
        }
        distribution.append(test_item)
    else:
        print(f"Warning: metadata_test.csv not found in {dataset_dir}")
        test_record_count = 0
    
    # Process validation set if it exists
    val_path = os.path.join(dataset_dir, 'metadata_val.csv')
    val_record_count = 0
    if os.path.exists(val_path):
        print(f"Processing validation dataset: {val_path}")
        val_hash = get_file_hash(val_path)
        val_size = get_file_size(val_path)
        val_record_count = count_records(val_path)
        
        val_item = {
            "@type": [
                "cr:FileObject",
                "schema:MediaObject",
                "schema:DataDownload"
            ],
            "@id": f"datasets/{dataset_name}/metadata_val.csv",
            "name": "metadata_val.csv",
            "description": f"Validation dataset for {dataset_name}",
            "contentUrl": f"{github_repo}/raw/main/datasets/{dataset_name}/metadata_val.csv",
            "encodingFormat": "text/csv",
            "sha256": val_hash,
            "dateModified": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "contentSize": f"{val_size} bytes",
            "inLanguage": "en"
        }
        distribution.append(val_item)
    
    # Update the distribution field
    template['distribution'] = distribution
    
    # Update record count and file count
    total_records = dev_record_count + test_record_count + val_record_count
    template['recordCount'] = total_records
    template['fileCount'] = len(distribution)
    
    # Update data splits
    data_splits = []
    if dev_record_count > 0:
        data_splits.append({
            "@type": "cr:DataSplit",
            "name": "train",
            "description": "Training data split",
            "recordCount": dev_record_count,
            "splits": [
                {
                    "@type": "schema:PropertyValue",
                    "propertyID": "train",
                    "value": "train"
                }
            ]
        })
    
    if val_record_count > 0:
        data_splits.append({
            "@type": "cr:DataSplit",
            "name": "validation",
            "description": "Validation data split",
            "recordCount": val_record_count,
            "splits": [
                {
                    "@type": "schema:PropertyValue",
                    "propertyID": "validation",
                    "value": "validation"
                }
            ]
        })
    
    if test_record_count > 0:
        data_splits.append({
            "@type": "cr:DataSplit",
            "name": "test",
            "description": "Test data split",
            "recordCount": test_record_count,
            "splits": [
                {
                    "@type": "schema:PropertyValue",
                    "propertyID": "test",
                    "value": "test"
                }
            ]
        })
    
    template['dataSplits'] = data_splits
    
    # Save the file
    output_path = os.path.join(dataset_dir, 'croissant.jsonld')
    with open(output_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"Successfully created {output_path}")
    print(f"Total records: {total_records}")
    print(f"Total files: {len(distribution)}")

if __name__ == "__main__":
    main()
