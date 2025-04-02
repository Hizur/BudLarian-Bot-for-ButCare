# data_loader.py
import json
import os

def load_data(filepath):
    """Loads JSON data from a file with robust error handling."""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}. Returning empty list.")
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading data from {filepath}: {e}")
        return []

def load_strains_data(filepath):
    return load_data(filepath)

def load_clinics_data(filepath):
    return load_data(filepath)

def ensure_file_exists(filepath, default_content="[]"):
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(default_content)
        print(f"Created file at {filepath} with default content.")