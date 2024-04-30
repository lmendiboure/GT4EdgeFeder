import random
import threading
import time
import csv
from datetime import datetime
from kubernetes import client, config, watch
from functions.utils import load_config, convert_memory_usage_to_megabytes, parse_memory_string, write_to_csv     
import os   

def node_selector(available_nodes):
	random.choice(available_nodes)

# Function to get the list of available nodes
def get_available_nodes(api_instance):
    nodes = api_instance.list_node().items
    return [node.metadata.name for node in nodes]

# Function to get pod configuration and namespace from loaded config
def get_pod_config(config_data):
    pod_config = config_data['pods_config'][0]  # Assume only one pod config is present
    return {
        "name": pod_config["name"],  # Name of the pod
        "CPU": pod_config["CPU"],    # Set of CPU values in milli CPUs
        "RAM": pod_config["RAM"],    # Set of RAM values in Mi
        "namespace": config_data["namespace"]  # Namespace
    }
# Function to generate resource limits based on pod type
def generate_resources(pod_type, pod_config):
    cpu = random.choice(pod_config["CPU"])
    ram = random.choice(pod_config["RAM"])

    if pod_type == "guaranteed":
        return {
            "requests": {"cpu": f"{cpu}m",
                         "memory": f"{ram}Mi"},
            "limits": {"cpu": f"{cpu}m",  
                       "memory": f"{ram}Mi"}
        }
    elif pod_type == "burstable":
        return {
            "requests": {"cpu": f"{cpu//2}m",  # Half of limit for burstable
                         "memory": f"{ram//2}Mi"},
            "limits": {"cpu": f"{cpu}m",
                       "memory": f"{ram}Mi"}
        }
    else:  # Best-effort
        return {}
        
        
def get_pod_spec(namespace, pod_name, node_name, resources):
    """
    Generate the specification for the pod.

    Args:
    - namespace (str): The namespace for the pod.
    - pod_name (str): The name of the pod.
    - node_name (str): The name of the node where the pod will be scheduled.
    - resources (dict): The resource limits for the pod.

    Returns:
    - dict: The pod specification.
    """
    return {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": pod_name,
            "namespace": namespace
        },
        "spec": {
            "nodeName": node_name,
            "restartPolicy": "Never",
            "containers": [
                {
                    "name": "example-container",
                    "image": "python:3.9",
                    "command": ["python", "-u", "-c", "results = [1 + 1 for _ in range("8807684292")]"],
                    "resources": resources
                }
            ]
        }
    }

# Function to launch a pod on a random node 
def launch_pod(namespace, node_name, pod_config, pod_counter,api_instance):

    pod_type = random.choice(["guaranteed", "burstable", "besteffort"])
    resources = generate_resources(pod_type, pod_config)

    # Define pod name with type and counter
    pod_name = f"{pod_config['name']}-{pod_type[0]}{pod_type[1]}-{pod_counter}"

    # Check if pod name already exists, if yes, generate a new name
    while True:
        if api_instance.list_namespaced_pod(namespace=namespace, field_selector=f"metadata.name={pod_name}").items:
            pod_counter += 1
            pod_name = f"{pod_config['name']}-{pod_type[0]}{pod_type[1]}-{pod_counter}"
        else:
            break

    # Define pod specification
    pod_manifest = get_pod_spec(namespace, pod_name, node_name, resources)

    # Create the pod
    api_instance.create_namespaced_pod(namespace=namespace, body=pod_manifest)
    print(f"Pod launched on node {node_name} with type: {pod_type}")

    # Increment pod counter for the next pod
    pod_counter += 1
        
        
def run_pods():

    config_data = load_config("config.yaml")
    
    namespace = config_data["namespace"]
    
    pod_counter = 1  # Initialize pod counter
    
    pod_config = get_pod_config(config_data)

    config.load_kube_config()
    api_instance = client.CoreV1Api()

    # Get the list of available nodes
    available_nodes = get_available_nodes(api_instance)

    # Get pod config

    pod_config = get_pod_config(config_data)

    # Launch pods periodically
    while True:
        time.sleep(random.randint(3, 6))
        num_pods = random.randint(2, 5)  # Random number of pods to launch
        for _ in range(num_pods):
            node_name = node_selector(available_nodes)
            launch_pod(namespace, node_name, pod_config, pod_counter, api_instance)
