import requests
import json
import os
import csv
import hashlib
from datetime import datetime
from io import StringIO
from typing import List, Dict, Optional, Any, Tuple

def get_dataset_directories(
    owner: str = "chrissweet",
    repo: str = "registry_actions", 
    token: Optional[str] = None,
    base_path: str = "dataset"
) -> List[Dict[str, Any]]:
    """
    Get all directories under the datasets folder in a GitHub repository.
    
    Args:
        owner (str): GitHub repository owner
        repo (str): Repository name
        token (str, optional): GitHub personal access token
        base_path (str): Base directory path to search (default: 'dataset')
    
    Returns:
        List[Dict]: List of dataset directories with metadata
    """
    # Set up authentication headers
    headers = {
        'Accept': 'application/vnd.github+json'
    }
    if token:
        headers['Authorization'] = f'token {token}'
    
    # Build URL for the datasets directory
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{base_path}'
    
    try:
        # Make the request to get dataset directories
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception for error status codes
        
        # Parse JSON response
        contents = response.json()
        
        # Filter for directories only
        datasets = [item for item in contents if item['type'] == 'dir']
        
        # Add commit info to each dataset
        for dataset in datasets:
            # Get the latest commit for this specific directory
            commit_info = get_latest_commit_for_path(
                owner, repo, f"{base_path}/{dataset['name']}", token
            )
            if commit_info:
                dataset['latest_commit'] = commit_info
        
        return datasets
    
    except requests.exceptions.RequestException as e:
        print(f"Error accessing GitHub API: {e}")
        return []

def get_latest_commit_for_path(
    owner: str, 
    repo: str, 
    path: str, 
    token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get the latest commit information for a specific path in the repository.
    
    Args:
        owner (str): GitHub repository owner
        repo (str): Repository name
        path (str): Path to get commit for
        token (str, optional): GitHub personal access token
    
    Returns:
        Dict: Commit information including SHA, date, message, etc.
    """
    # Set up authentication headers
    headers = {
        'Accept': 'application/vnd.github+json'
    }
    if token:
        headers['Authorization'] = f'token {token}'
    
    # Build URL for commits API
    url = f'https://api.github.com/repos/{owner}/{repo}/commits'
    params = {
        'path': path,
        'per_page': 1  # Just get the latest commit
    }
    
    try:
        # Make the request
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        # Parse JSON response
        commits = response.json()
        
        if commits and len(commits) > 0:
            commit = commits[0]
            # Extract relevant information
            return {
                'sha': commit['sha'],
                'author': commit['commit']['author']['name'],
                'date': commit['commit']['author']['date'],
                'message': commit['commit']['message'],
                'url': commit['html_url']
            }
        return {}
    
    except requests.exceptions.RequestException as e:
        print(f"Error accessing GitHub commits API: {e}")
        return {}

def get_file_content(
    owner: str,
    repo: str,
    path: str,
    token: Optional[str] = None,
    ref: str = 'main'
) -> Optional[str]:
    """
    Get the content of a file from a GitHub repository.
    
    Args:
        owner (str): GitHub repository owner
        repo (str): Repository name
        path (str): Path to the file
        token (str, optional): GitHub personal access token
        ref (str): Branch or commit SHA reference
        
    Returns:
        Optional[str]: File content or None if not found
    """
    # Set up authentication headers
    headers = {
        'Accept': 'application/vnd.github.raw+json'
    }
    if token:
        headers['Authorization'] = f'token {token}'
    
    # Build URL for the file
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={ref}'
    
    try:
        # Make the request
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Return the raw content
        return response.text
    
    except requests.exceptions.RequestException as e:
        print(f"Error accessing file {path}: {e}")
        return None

def list_directory_files(
    owner: str,
    repo: str,
    path: str,
    token: Optional[str] = None,
    ref: str = 'main'
) -> List[Dict[str, Any]]:
    """
    List all files in a directory of a GitHub repository.
    
    Args:
        owner (str): GitHub repository owner
        repo (str): Repository name
        path (str): Path to the directory
        token (str, optional): GitHub personal access token
        ref (str): Branch or commit SHA reference
        
    Returns:
        List[Dict]: List of files with metadata
    """
    # Set up authentication headers
    headers = {
        'Accept': 'application/vnd.github+json'
    }
    if token:
        headers['Authorization'] = f'token {token}'
    
    # Build URL for the directory
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={ref}'
    
    try:
        # Make the request
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse JSON response
        contents = response.json()
        
        # Return all items
        return contents if isinstance(contents, list) else []
    
    except requests.exceptions.RequestException as e:
        print(f"Error listing directory {path}: {e}")
        return []

def parse_csv_content(content: str) -> List[Dict[str, Any]]:
    """
    Parse CSV content into a list of dictionaries.
    
    Args:
        content (str): CSV content as string
        
    Returns:
        List[Dict]: Parsed CSV data as list of dictionaries
    """
    csv_data = []
    try:
        csv_file = StringIO(content)
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            csv_data.append(row)
        return csv_data
    except Exception as e:
        print(f"Error parsing CSV content: {e}")
        return []

def detect_csv_schema(csv_data: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Detect the schema (column types) of a CSV file.
    
    Args:
        csv_data (List[Dict]): Parsed CSV data
        
    Returns:
        Dict: Mapping of column names to data types
    """
    if not csv_data:
        return {}
    
    schema = {}
    sample_row = csv_data[0]
    
    for column, value in sample_row.items():
        # Skip empty columns or values
        if not column or value is None or value == "":
            schema[column] = "string"
            continue
            
        # Try to infer the data type
        try:
            int(value)
            schema[column] = "integer"
            continue
        except ValueError:
            pass
        
        try:
            float(value)
            schema[column] = "number"
            continue
        except ValueError:
            pass
        
        # Check if it's a date
        date_formats = ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"]
        is_date = False
        for date_format in date_formats:
            try:
                datetime.strptime(value, date_format)
                schema[column] = "date"
                is_date = True
                break
            except ValueError:
                pass
                
        if is_date:
            continue
            
        # Default to string
        schema[column] = "string"
    
    return schema

def generate_croissant_metadata(
    dataset_dir: Dict[str, Any],
    owner: str,
    repo: str,
    token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate Croissant metadata for a dataset.
    
    Args:
        dataset_dir (Dict): Dataset directory metadata
        owner (str): GitHub repository owner
        repo (str): Repository name
        token (str, optional): GitHub personal access token
        
    Returns:
        Dict: Croissant metadata
    """
    dataset_name = dataset_dir['name']
    dataset_path = dataset_dir['path']
    commit_info = dataset_dir.get('latest_commit', {})
    commit_sha = commit_info.get('sha', 'main')
    commit_date = commit_info.get('date', datetime.now().isoformat())
    
    # List all files in the dataset directory
    files = list_directory_files(owner, repo, dataset_path, token, commit_sha)
    
    # Find metadata files
    metadata_files = {
        'train': next((f for f in files if f['name'] == 'metadata_dev.csv'), None),
        'validation': next((f for f in files if f['name'] == 'metadata_val.csv'), None),
        'test': next((f for f in files if f['name'] == 'metadata_test.csv'), None),
        'labels': next((f for f in files if f['name'] == 'labels.csv'), None),
        'projects': next((f for f in files if f['name'] == 'projects.csv'), None)
    }
    
    # Fetch and parse metadata files
    datasets = {}
    for key, file_meta in metadata_files.items():
        if file_meta:
            file_content = get_file_content(owner, repo, file_meta['path'], token, commit_sha)
            if file_content:
                datasets[key] = {
                    'file': file_meta,
                    'content': file_content,
                    'data': parse_csv_content(file_content)
                }
    
    # Create distribution information
    distributions = []
    for key, dataset in datasets.items():
        if not dataset['data']:
            continue
            
        # Detect schema
        schema = detect_csv_schema(dataset['data'])
        
        # Generate content URL with specific commit SHA
        content_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{commit_sha}/{dataset['file']['path']}"
        
        # Calculate SHA-256 hash for the file content
        content_hash = hashlib.sha256(dataset['content'].encode()).hexdigest()
        
        # Create distribution entry
        distribution = {
            "@type": "cr:FileObject",
            "@id": dataset['file']['path'],
            "name": dataset['file']['name'],
            "contentUrl": content_url,
            "encodingFormat": "text/csv",
            "sha256": content_hash
        }
        distributions.append(distribution)
    
    # Build the data schema based on the training data
    data_schema = []
    if 'train' in datasets and datasets['train']['data']:
        train_schema = detect_csv_schema(datasets['train']['data'])
        for column, data_type in train_schema.items():
            field = {
                "@type": "cr:TableSchema/column",
                "name": column,
                "description": f"Column: {column}"
            }
            
            # Map data types to schema.org types
            if data_type == "integer":
                field["dataType"] = "integer"
            elif data_type == "number":
                field["dataType"] = "float"
            elif data_type == "date":
                field["dataType"] = "date"
            else:
                field["dataType"] = "string"
                
            data_schema.append(field)
    
    # Count total samples
    total_samples = sum(len(dataset['data']) for dataset in datasets.values())
    
    # Create Croissant metadata
    metadata = {
        "@context": {
            "@language": "en",
            "cr": "http://mlcommons.org/croissant/",
            "schema": "http://schema.org/",
            "@vocab": "http://mlcommons.org/croissant/"
        },
        "@type": "cr:Dataset",
        "name": dataset_name,
        "description": f"Dataset: {dataset_name} from {owner}/{repo}",
        "version": commit_sha[:7],  # Use first 7 chars of commit as version
        "datePublished": commit_date,
        "license": "https://www.apache.org/licenses/LICENSE-2.0",
        "creator": {
            "@type": "schema:Person",
            "name": commit_info.get('author', owner)
        },
        "citations": [],
        "distribution": distributions,
        "recordCount": total_samples,
        "fileCount": len(distributions),
        "datasetSchema": {
            "@type": "cr:TableSchema",
            "columns": data_schema
        }
    }
    
    # Add data splits if we have training, validation and test sets
    if 'train' in datasets or 'validation' in datasets or 'test' in datasets:
        metadata["dataSplits"] = []
        
        if 'train' in datasets:
            metadata["dataSplits"].append({
                "@type": "cr:DataSplit",
                "name": "train",
                "description": "Training data split",
                "recordCount": len(datasets['train']['data'])
            })
            
        if 'validation' in datasets:
            metadata["dataSplits"].append({
                "@type": "cr:DataSplit",
                "name": "validation",
                "description": "Validation data split",
                "recordCount": len(datasets['validation']['data'])
            })
            
        if 'test' in datasets:
            metadata["dataSplits"].append({
                "@type": "cr:DataSplit",
                "name": "test",
                "description": "Test data split",
                "recordCount": len(datasets['test']['data'])
            })
    
    return metadata

if __name__ == "__main__":
    # Get GitHub token from environment variable for security
    token = os.environ.get("GITHUB_TOKEN")
    
    # Repository info
    owner = "chrissweet"
    repo = "registry_actions"
    
    # Output directory for Croissant metadata
    output_dir = "croissant_metadata"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all dataset directories
    datasets = get_dataset_directories(owner, repo, token=token)
    
    print(f"Found {len(datasets)} datasets")
    
    # Generate Croissant metadata for each dataset
    for dataset in datasets:
        dataset_name = dataset['name']
        print(f"Generating Croissant metadata for dataset: {dataset_name}")
        
        # Generate metadata
        croissant_metadata = generate_croissant_metadata(dataset, owner, repo, token)
        
        # Save metadata to file
        output_file = os.path.join(output_dir, f"{dataset_name}_croissant.json")
        with open(output_file, "w") as f:
            json.dump(croissant_metadata, f, indent=2)
        
        print(f"  Saved metadata to {output_file}")
    
    print(f"Croissant metadata generation complete!")
