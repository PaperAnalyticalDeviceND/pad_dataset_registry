#!/usr/bin/env python3
"""
Validate Croissant JSONLD files against the official schema.
"""

import json
import os
import glob
import requests

# Base paths
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
DATASETS_DIR = os.path.join(REPO_ROOT, 'datasets')
OUTPUT_DIR = os.path.join(REPO_ROOT, 'docs', '_data')

# Schema URL
SCHEMA_URL = 'https://raw.githubusercontent.com/mlcommons/croissant/main/schema/croissant.schema.json'
SCHEMA_PATH = os.path.join(OUTPUT_DIR, 'croissant_schema.json')

def download_schema():
    """Download the Croissant schema if it doesn't exist."""
    if not os.path.exists(SCHEMA_PATH):
        print(f"Downloading Croissant schema from {SCHEMA_URL}")
        try:
            response = requests.get(SCHEMA_URL)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(SCHEMA_PATH), exist_ok=True)
            with open(SCHEMA_PATH, 'w') as f:
                f.write(response.text)
            print(f"Schema saved to {SCHEMA_PATH}")
            
            return json.loads(response.text)
        except Exception as e:
            print(f"Error downloading schema: {str(e)}")
            return None
    else:
        try:
            with open(SCHEMA_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading schema: {str(e)}")
            return None

def validate_basic(data, schema_data):
    """Basic validation without external dependencies."""
    # Check required properties at the root level
    required_props = ['@context', '@id', '@type', 'name', 'description']
    missing_props = [prop for prop in required_props if prop not in data]
    
    if missing_props:
        return False, f"Missing required properties: {', '.join(missing_props)}"
    
    # Check @type contains required values
    required_types = ['cr:Dataset', 'schema:Dataset']
    if '@type' in data and isinstance(data['@type'], list):
        missing_types = [t for t in required_types if t not in data['@type']]
        if missing_types:
            return False, f"Missing required types: {', '.join(missing_types)}"
    else:
        return False, "Invalid or missing @type property"
    
    return True, "Basic validation passed"

def main():
    """Main function to validate Croissant files."""
    schema_data = download_schema()
    if not schema_data:
        print("Using basic validation instead")
    
    # Find all Croissant files
    croissant_files = glob.glob(os.path.join(DATASETS_DIR, '*/croissant.jsonld'))
    valid_count = 0
    invalid_count = 0
    
    for croissant_file in croissant_files:
        dataset_name = os.path.basename(os.path.dirname(croissant_file))
        
        try:
            with open(croissant_file, 'r') as f:
                data = json.load(f)
            
            # If we have the schema, use it for validation
            if schema_data:
                try:
                    from jsonschema import validate
                    validate(instance=data, schema=schema_data)
                    valid = True
                    message = "Validation successful"
                except ImportError:
                    valid, message = validate_basic(data, schema_data)
                except Exception as e:
                    valid = False
                    message = str(e)
            else:
                valid, message = validate_basic(data, schema_data)
            
            if valid:
                print(f"✅ {dataset_name}: {message}")
                valid_count += 1
            else:
                print(f"❌ {dataset_name}: {message}")
                invalid_count += 1
                
        except Exception as e:
            print(f"❌ Error processing {croissant_file}: {str(e)}")
            invalid_count += 1
    
    print(f"\nValidation complete: {valid_count} valid, {invalid_count} invalid")
    return valid_count, invalid_count

if __name__ == "__main__":
    main()
