import os
import csv
import yaml
import time
from kubernetes import client, config, watch
from datetime import datetime
from functions.utils import load_config, convert_memory_usage_to_megabytes, parse_memory_string, write_to_csv    
import psutil    

def watch_pods():
    """
    Watch pods in a specified namespace and log their phase transitions to a CSV file.
    """
    try: 

        # Load configuration data from the YAML file
        config_data = load_config("config.yaml")
        # Get the namespace from the configuration data
        namespace = config_data['namespace']
        
        # Get the results file for pods from the configuration data, default to 'data.csv'
        results_file_pods = config_data.get('results_file_pods', 'data.csv')

        # Load Kubernetes configuration from default location
        config.load_kube_config()

        # Create a client to interact with the Kubernetes API
        api_instance = client.CoreV1Api()

        # Initialize a watch stream
        w = watch.Watch()

        # Iterate over events in the watch stream
        for event in w.stream(api_instance.list_namespaced_pod, namespace=namespace):
            # Extract pod name and phase from the event
            pod_name = event['object'].metadata.name
            pod_phase = event['object'].status.phase
            node_name = event['object'].spec.node_name  # Get the node name

            # Get current timestamp with milliseconds
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            # Check the phase of the pod and take appropriate action
            if pod_phase == "Pending":
                print(f"Pod {pod_name} is now Pending.")
                write_to_csv(results_file_pods, [timestamp, pod_name, "Pending"])


            elif pod_phase == "Running":
                # Write timestamp, pod name, and phase to the CSV file
                print(f"Pod {pod_name} is now Running on Node {node_name}.")
                write_to_csv(results_file_pods, [timestamp, pod_name, "Running", node_name])

            elif pod_phase == "Failed" or pod_phase == "Succeeded":
                print(f"Pod {pod_name} is now Completed.")
                # Write timestamp, pod name, and phase to the CSV file
                write_to_csv(results_file_pods, [timestamp, pod_name, "Terminated"])

    except Exception as e:
        # Handle any exceptions and print error message
        print(f"Error watching pods:", e)
        
        

def get_cpu_usage_percent():
    """Get the CPU usage percentage."""
    return psutil.cpu_percent(interval=1)

def get_ram_usage_percent():
    """Get the RAM usage percentage."""
    return psutil.virtual_memory().percent

def get_cluster_nodes_usage():
    """Get CPU and RAM usage for all nodes in the Kubernetes cluster."""
    config.load_kube_config()  

    v1 = client.CoreV1Api()
    nodes = v1.list_node().items

    node_usage = {}

    for node in nodes:
        node_name = node.metadata.name
        node_ip = node.status.addresses[0].address
        node_cpu_usage = get_cpu_usage_percent()
        node_ram_usage = get_ram_usage_percent()
        node_usage[node_name] = {
            'ip': node_ip,
            'cpu_usage_percent': node_cpu_usage,
            'ram_usage_percent': node_ram_usage
        }

    return node_usage


def get_ephemeral_storage_usage(config_data):
    """Get the ephemeral storage usage for all nodes in the Kubernetes cluster."""
    try:
        config.load_kube_config()  
        namespace = config_data['namespace']
        
        disk_size = config_data['disk_size']
        
        nodes_number = config_data['nodes_number']
        
        storage_size = disk_size / nodes_number
        
        api_instance = client.CoreV1Api()
        
        nodes = api_instance.list_node().items

        storage_data = {}

        for node in nodes:
            node_name = node.metadata.name
            total_storage_used = 0

            pods = api_instance.list_namespaced_pod(namespace=namespace, field_selector=f"spec.nodeName={node_name}").items

            for pod in pods:
                if pod.status.phase == "Running":
                    for pod_config in config_data.get('pods_config', []):
                        if pod.metadata.name.startswith(pod_config['name']):
                            pod_storage_usage = pod_config['storage']
                            total_storage_used += pod_storage_usage

            storage_data[node_name] = (total_storage_used/storage_size)*100

        return storage_data

    except Exception as e:
        print(f"Error retrieving ephemeral storage utilization information:", e)
        return None


def get_nodes_utilization(output_file=None):
    """Get CPU, RAM, and ephemeral storage utilization for all nodes in the Kubernetes cluster."""
    try:
    
    	# Retrieve infos from config file
        config_data = load_config("config.yaml")   
        
        results_file_nodes = config_data.get('results_file_nodes', 'data.csv') if output_file is None else output_file

	# Compute CPU and RAM usage
        node_usage = get_cluster_nodes_usage()
        
        # Compute storage usage
        storage_data = get_ephemeral_storage_usage(config_data)
        print(storage_data)
        timestamp = datetime.now()

        if node_usage:
            for node_name, node_data in node_usage.items():
                cpu_utilization_rate = node_data['cpu_usage_percent']
                ram_utilization_rate = node_data['ram_usage_percent']
                storage_usage = storage_data.get(node_name, 0)
                write_to_csv(results_file_nodes, (timestamp, node_name, cpu_utilization_rate, ram_utilization_rate, storage_usage))

    except Exception as e:
        print(f"Error retrieving resource utilization and storage information:", e)

def watch_nodes():
    """
    Get nodes data for a specific namespace.Complete data result file every second.
    """
    config_data = load_config("config.yaml")
    results_file_nodes = config_data.get('results_file_nodes', 'data.csv') 
    while True:
        get_nodes_utilization(output_file=results_file_nodes)
        time.sleep(1)
