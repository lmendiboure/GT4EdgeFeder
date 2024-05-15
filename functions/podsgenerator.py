import random
import threading
import time
import csv
import math
from datetime import datetime
from kubernetes import client, config, watch
from functions.utils import load_config, convert_memory_usage_to_megabytes, parse_memory_string, write_to_csv, load_dataset     
import os   
	
# Function to get the list of available nodes
def get_available_nodes(api_instance):
    nodes = api_instance.list_node().items
    return [node.metadata.name for node in nodes]
    
# Function to determine the latency associated with data transmission for a given pod.    
def get_ran_infos_for_pods(config_data,pod_config):
    lines=load_dataset(config_data['dataset'])
    random_line = random.choice(lines)
    data = random_line.strip().split(',')
    traffic_load = int(data[11])
    latency = int(data[12])
    return math.ceil((pod_config["transmission_uplink"]+pod_config["transmission_downlink"])/(traffic_load*1000)+latency)
    
    
# Function to determine the priority class of a pod. Priority class is directly linked to the type of pod. Not useful in GT paper.    
def get_pod_priority_class(pod_type):
    priority_class=None        
    if pod_type == "guaranteed":
        priority_class = "high-priority"
    elif pod_type == "burstable":
        priority_class = "medium-priority"
    else:
        priority_class = "low-priority"
    return priority_class

# Function to get pod configuration and namespace from loaded config
def get_pod_config(config_data):
    app_pod = random.randint(0, 2)
    pod_config = config_data['pods_config'][app_pod]
    return {
        "name": pod_config["name"],  # Name of the pod
        "CPU": pod_config["CPU"],    # CPU value in milli CPUs
        "RAM": pod_config["RAM"],    # RAM value in Mi
        "instructions":pod_config["instructions"],
        "namespace": config_data["namespace"],  # Namespace
        "transmission_uplink": pod_config["transmission_uplink"], # Bits to transmit in Uplink
        "transmission_downlink": pod_config["transmission_downlink"] # Bits to transmit in Downlink
    }
# Function to generate resource limits based on pod type
def generate_resources(pod_type, pod_config):
    cpu = pod_config["CPU"]
    ram = pod_config["RAM"]

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
        
        
def get_pod_spec(config_data, pod_name, node_name, pod_type, pod_config):
    """
    Generate the specification for the pod.

    Args:
    - namespace (str): The namespace for the pod.
    - pod_name (str): The name of the pod.
    - node_name (str): The name of the node where the pod will be scheduled.
    - resources (dict): The resource limits for the pod.
    - priority_class (str): The name of the priority class to use.

    Returns:
    - dict: The pod specification.
    """
    instructions = pod_config["instructions"]
    resources = generate_resources(pod_type, pod_config)
    delay = str(get_ran_infos_for_pods(config_data, pod_config))
    namespace = config_data["namespace"]
    # Priority class could be useful is pods should be prioritized at execution (ie multiple queues), line below enables to retrieve information regarding priority class
    # priority_class = get_pod_priority_class(pod_type) 
    spec = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": pod_name,
            "namespace": namespace,
            "annotations": {
                "transmission_delay": delay
            }
        },
        "spec": {
            "nodeName": node_name,
            "restartPolicy": "Never",
            "containers": [
                {
                    "name": "example-container",
                    "image": "python:3.9",
                   "command": ["python", "-u", "-c", f"results = [1 + 1 for _ in range({instructions})]"],
                    "resources": resources
                }
            ]
        }
    }
    # Add priority class to pod spec
    #if priority_class:
    #    spec['spec']['priorityClassName'] = priority_class
    
    return spec    

# Function to launch a pod on a random node 
def launch_pod(config_data, node_name, pod_config, pod_counter,api_instance):
    
    namespace = config_data["namespace"]
    pod_type = random.choice(["guaranteed", "burstable", "besteffort"])
    
    # Define pod name with type and counter
    pod_name = f"{pod_config['name']}-{pod_type[0]}{pod_type[1]}-{pod_counter}"
    
    # Define pod specification
    pod_manifest = get_pod_spec(config_data, pod_name, node_name, pod_type, pod_config)

    # Create the pod
    api_instance.create_namespaced_pod(namespace=namespace, body=pod_manifest)
    print(f"Pod launched on node {node_name} with type: {pod_type}")
        
        
def run_pods(node_selection_func):

    config_data = load_config("config.yaml")
    
    pod_counter = 1  # Initialize pod counter

    config.load_kube_config()
    api_instance = client.CoreV1Api()

    # Get the list of available nodes
    available_nodes = get_available_nodes(api_instance)

    # Launch pods periodically
    while True:
        time.sleep(random.randint(1, 3))
        num_pods = random.randint(3, 6)  # Random number of pods to launch
        for _ in range(num_pods):
            node_name = node_selection_func(available_nodes)
            # Get pod config
            pod_config = get_pod_config(config_data)
            get_ran_infos_for_pods(config_data,pod_config)
            launch_pod(config_data, node_name, pod_config, pod_counter, api_instance)
            # Increment pod counter for the next pod
            pod_counter += 1
