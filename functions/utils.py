import os
import csv
import yaml
import time
from math import ceil
from kubernetes import client, config, watch
from datetime import datetime


def rename_results_files(experiment_number):
    """Rename all result files to include the experiment number."""
    
    # Load configuration data from the YAML file
    config_data = load_config("config.yaml")
    
    # Get experiment files from the configuration data
    
    results_file_pods = config_data.get('results_file_pods', 'data.csv')
    results_file_nodes = config_data.get('results_file_nodes', 'data.csv')
    
    basep, extp = os.path.splitext(results_file_pods) 
    
    new_pods_file= f"{basep}_experiment_{experiment_number}{extp}"
    
    
    basen, extn = os.path.splitext(results_file_nodes) 
    
    new_nodes_file= f"{basen}_experiment_{experiment_number}{extn}"
    
    os.rename(results_file_pods, new_pods_file)
    
    os.rename(results_file_nodes, new_nodes_file)  

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
        lines = file.readlines()[1:]
           
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
    return len(lines)-1    

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
    data=["timestamp", "pod_name", "Status", "initial_node", "running_node", "ran_delay", "inter_node_delay"]
    write_to_csv(results_file_pods, data)
    clean_csv(results_file_nodes)
    data=["timestamp", "node_name", "CPU", "RAM", "storage"]
    write_to_csv(results_file_nodes, data)

def get_selfish_ratio(config_data,nodename):
    """Get the percentage of the resources of the node that will only be used by this node and will not be used by the federation."""
    selfish_ratio=0
    # Find node in config_data
    for node in config_data["nodes_config"]:
        if node["id"] == nodename:
            selfish_ratio = node["selfish-ratio"]
    return selfish_ratio
    

def get_processing_delay(config_data,nodename,podtype,podclass):
    """Get the latency associated with the processing of a pod on a given node (ie pod processing time)."""
    delay=0
    # Find node in config_data
    for node in config_data["nodes_config"]:
        if node["id"] == nodename:
            # Find corresponding application
            for application in node["average-processing-delay"]:
                if application["pod-name"] == podtype:
                    # Sum latency + time to transmit data (uplink + downlink)
                    delay = application[podclass[:2]]
    return delay

def get_inter_node_delay(config_data,origin_node,destination_node,data):
    """Get the latency associated with the transmission of data between nodes (ie pod transfer)."""
    delay=0
    # Find node in config_data
    for node in config_data["nodes_config"]:
        if node["id"] == origin_node:
            # Find destination node
            for connection in node["connections"]:
                if connection["target_node"] == destination_node:
                    # Sum latency + time to transmit data (uplink + downlink)
                    delay = ceil(connection["latency"] + data/connection["bandwidth"])
    return delay

def order_nodes_by_delay(config_data, nodes, initial_node, data, podtype, podclass, include_initial_node=True):

    """Get the list of nodes that can manage a given pod with an ordering based on the processing delay of each node."""

    updated_list = {}
    
    # Depending on the solution chose, the initial node should or should not ge considered
    if not include_initial_node:
        for node_name in nodes.keys():
            if node_name !=initial_node:
                updated_list[node_name]=nodes[node_name] 
       
        print (updated_list)    
    else:
        updated_list=nodes    
        
    for node_name in updated_list.keys():
        updated_list[node_name]["delay"] = get_processing_delay(config_data,node_name,podtype,podclass)
        if node_name != initial_node:
            updated_list[node_name]["delay"]+= get_inter_node_delay(config_data,initial_node, node_name,data)
    
    
    sorted_nodes = sorted(updated_list.keys(), key=lambda key: updated_list[key]['delay'])  

    return sorted_nodes
    
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
        
# Function to get the list of available nodes
def get_available_nodes(api_instance):
    nodes = api_instance.list_node().items
    return [node.metadata.name for node in nodes]


# Function to get the resources available on a given node (using node index in config file)
def get_node_resources_infos(config_data, index):
    disk_size = config_data['disk_size']
        
    nodes_number = config_data['nodes_number']
        
    available_cpu = config_data['cpus']*nodes_number
        
    available_ram = config_data['memory']*nodes_number
        
    storage_size = disk_size
    
    node_cpu = available_cpu*config_data['nodes_config'][index]['CPU_percentage']
    node_ram=available_ram*config_data['nodes_config'][index]['RAM_percentage']
    node_storage= storage_size*config_data['nodes_config'][index]['storage_percentage']
    
    return node_cpu, node_ram, node_storage
  

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
