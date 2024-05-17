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
    
def load_dataset(filename):
    """
    Load dataset for ran/pods.

    Args:
        filename (str): Path to the RAN/Pods dataset file.

    Returns:
        dict: ran/pods dataset.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    file_path = os.path.join(project_root, "data", filename)
    with open(file_path, 'r') as file:
        lines = file.readlines()
           
    return lines

def compute_pods_number(filename):
    """
    Compute the number of pods that have to run in the current experiment.

    Args:
        filename (str): Path to the Pods dataset file.

    Returns:
        int: number of pods in the dataset.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    file_path = os.path.join(project_root, "data", filename)
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return len(lines)    

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

def clean_csv(filename):
    """
    Clean (empty) a CSV file.

    Args:
        filename (str): Path to the CSV file to be cleaned.
    """
    # Verify if file exists
    if os.path.exists(filename):
        # Open file in write mode
        with open(filename, 'w', newline='') as file:
            pass  # Just close it
    
def clean_experiment_files():
    """
    Clean all experiment files (pods + nodes).

    Returns:
        None
    """
    
    # Load configuration data from the YAML file
    config_data = load_config("config.yaml")
    
    # Get experiment files from the configuration data
    
    results_file_pods = config_data.get('results_file_pods', 'data.csv')
    results_file_nodes = config_data.get('results_file_nodes', 'data.csv') 
    
    # Empty Files  
    clean_csv(results_file_pods)
    clean_csv(results_file_nodes)

def node_name_finder(node_number):
    """
    Get node name from node number

    Args:
        node number (int): Number of the node
    """
    number=str(node_number)
    if node_number==1:
    	return "minikube"
    elif node_number <10:
        return f"minikube-m0{number}"    
    else:
        return f"minikube-m{number}"
    
    
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
        
        
def delete_pods():
    """
    Delete all pods in the specified namespace.

    Args:
        namespace (str): Namespace to delete pods from.

    Returns:
        None
    """
    
    # Load configuration data from the YAML file
    config_data = load_config("config.yaml")
    # Get the namespace from the configuration data
    namespace = config_data['namespace']
    # Load Kubernetes configuration from default location
    config.load_kube_config()

    # Create a client to interact with the Kubernetes API
    api_instance = client.CoreV1Api()

    # List all pods in the specified namespace
    pods = api_instance.list_namespaced_pod(namespace=namespace).items

    # Iterate over each pod and delete it
    for pod in pods:
        # Delete the pod
        api_instance.delete_namespaced_pod(name=pod.metadata.name, namespace=namespace, grace_period_seconds=0)        
