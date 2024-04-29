import os
import csv
import yaml
import time
from kubernetes import client, config, watch
from datetime import datetime

def load_config(filename):
    """
    Load configuration from YAML file.

    Args:
        filename (str): Path to the YAML configuration file.

    Returns:
        dict: Configuration data.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    config_file_path = os.path.join(project_root, "config", filename)
    with open(config_file_path, 'r') as file:
        config_data = yaml.safe_load(file)
    return config_data
    
def convert_memory_usage_to_megabytes(memory_usage_bytes):
    """
    Convert memory usage from bytes to megabytes.

    Args:
        memory_usage_bytes (int): Memory usage in bytes.

    Returns:
        float: Memory usage in megabytes.
    """
    return memory_usage_bytes / (1024 ** 2)
    
    
def write_to_csv(filename, data):
    """
    Write data to a CSV file.

    Args:
        filename (str): Path to the CSV file.
        data (list of tuples): Data to be written to the CSV file.
    """
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)
    
    
def parse_memory_string(memory_string):
    """
    Parse a memory string and convert it to bytes.

    Args:
        memory_string (str): Memory string in Kubernetes format (e.g., "64Mi").

    Returns:
        int: Memory value in bytes.
    """
    if memory_string.endswith("Ki"):
        return int(memory_string[:-2]) * 1024
    elif memory_string.endswith("Mi"):
        return int(memory_string[:-2]) * 1024 ** 2
    elif memory_string.endswith("Gi"):
        return int(memory_string[:-2]) * 1024 ** 3
    elif memory_string.endswith("Ti"):
        return int(memory_string[:-2]) * 1024 ** 4
    else:
        raise ValueError("Invalid memory string format")
        
