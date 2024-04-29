import os
import csv
import yaml
import time
from kubernetes import client, config, watch
from datetime import datetime
from functions.utils import load_config, convert_memory_usage_to_megabytes, parse_memory_string, write_to_csv        

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
            # Get current timestamp with milliseconds
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            # Check the phase of the pod and take appropriate action
            if pod_phase == "Pending":
                print(f"Pod {pod_name} is now Pending.")

            elif pod_phase == "Running":
                # Write timestamp, pod name, and phase to the CSV file
                print(f"Pod {pod_name} is now Running.")
                write_to_csv(results_file_pods, [timestamp, pod_name, "Running"])

            elif pod_phase == "Failed" or pod_phase == "Succeeded":
                print(f"Pod {pod_name} is now Completed.")
                # Write timestamp, pod name, and phase to the CSV file
                write_to_csv(results_file_pods, [timestamp, pod_name, "Terminated"])

    except Exception as e:
        # Handle any exceptions and print error message
        print(f"Error watching pods:", e)


def get_storage_and_resource_utilization_for_all_nodes(output_file=None):
    """
    Get storage usage, CPU, and RAM utilization for all nodes in the Kubernetes cluster. Write results in a CSV file format IF file given. Otherwise, it is sent back as data.
    """
    try:

        config_data = load_config("config.yaml")
        
        namespace = config_data['namespace']
        disk_size_gb = config_data.get('disk_size', 0)  # Disk size in GB
        nodes_number = config_data.get('nodes_number', 1)  # Number of nodes
        memory_per_node_mb = config_data.get('memory', 0)  # Memory per node in MB
        cpus_per_node = config_data.get('cpus', 0)  # CPUs per node
        
        results_file_nodes = config_data.get('results_file_nodes', 'data.csv') if output_file is None else output_file  # File to load results

        # Calculate base storage capacity per node
        base_storage_per_node_gb = disk_size_gb / nodes_number

        # Load Kubernetes configuration
        config.load_kube_config()

        # Create a client to interact with the Kubernetes API
        api_instance = client.CoreV1Api()

        # Get the list of nodes in the cluster
        nodes = api_instance.list_node().items

        # Data list to store the data for CSV
        data = []

        # Get the timestamp once
        timestamp = datetime.now()

        # Iterate over each node in the cluster
        for node in nodes:
            node_name = node.metadata.name
            total_memory_usage_bytes = 0
            total_cpu_usage_millicores = 0

            # Get the list of pods running on the current node
            pods = api_instance.list_namespaced_pod(namespace=namespace, field_selector=f"spec.nodeName={node_name}").items

            # Iterate over each pod and retrieve resource usage
            for pod in pods:
                if pod.status.phase == "Running":  # Only consider pods in "Running" phase
                    for container in pod.spec.containers:
                        # Memory usage
                        memory_request = container.resources.requests.get("memory", "0Ki")
                        memory_request_bytes = parse_memory_string(memory_request)
                        total_memory_usage_bytes += memory_request_bytes

                        # CPU usage
                        cpu_request = container.resources.requests.get("cpu", "0")
                        cpu_request_millicores = int(cpu_request[:-1]) if cpu_request.endswith("m") else int(cpu_request)
                        total_cpu_usage_millicores += cpu_request_millicores

            # Convert memory usage to megabytes
            total_memory_usage_mb = convert_memory_usage_to_megabytes(total_memory_usage_bytes)

            # Calculate memory utilization rate
            memory_utilization_rate = (total_memory_usage_mb / memory_per_node_mb) * 100

            # Calculate CPU utilization rate
            cpu_utilization_rate = (total_cpu_usage_millicores / (cpus_per_node * 1000)) * 100

            # Get storage usage for pods on the node
            total_storage_used = 0
            for pod_config in config_data.get('pods_config', []):
                pod_name_prefix = pod_config['name']
                field_selector = f"spec.nodeName={node_name}"
                pods = api_instance.list_namespaced_pod(namespace, field_selector=field_selector).items

                # Calculate total storage used by pods corresponding to the current node
                for pod in pods:
                    if pod.status.phase == "Running":  # Only consider pods in "Running" phase	
                        if pod.metadata.name.startswith(pod_name_prefix):
                            pod_storage = pod_config['storage']
                            total_storage_used += pod_storage

            # Calculate storage related values
            storage_used_percent = (total_storage_used / base_storage_per_node_gb) * 100
            storage_available_percent = 100 - storage_used_percent

            # Append data to the list
            data.append((node_name, cpu_utilization_rate, memory_utilization_rate, storage_used_percent))

        # Write data to CSV with the same timestamp for all nodes
        if output_file:
            for node_data in data:
                write_to_csv(results_file_nodes, (timestamp,) + node_data)
        else:
            return data

    except Exception as e:
        print(f"Error retrieving resource utilization and storage information:", e)


def watch_nodes():
    """
    Get nodes data for a specific namespace.Complete data result file every second.
    """
    config_data = load_config("config.yaml")
    results_file_nodes = config_data.get('results_file_nodes', 'data.csv') 
    while True:
        get_storage_and_resource_utilization_for_all_nodes(output_file=results_file_nodes)
        time.sleep(1)
