import random
import threading
import time
import csv
import math
from datetime import datetime
from kubernetes import client, config, watch
from functions.utils import load_config, convert_memory_usage_to_megabytes, parse_memory_string, write_to_csv, load_dataset, get_inter_node_delay     
import os   
    
# Function to determine the priority class of a pod. Priority class is directly linked to the type of pod. Not useful in GT paper.    
def get_pod_priority_class(pod_class):
    priority_class=None        
    if pod_class == "guaranteed":
        priority_class = "high-priority"
    elif pod_class == "burstable":
        priority_class = "medium-priority"
    else:
        priority_class = "low-priority"
    return priority_class


def get_pod_config_by_type(pods_config, pod_name):
    """
    Get pod configuration by name.

    Args:
        pods_config (list of dicts): List of pod configurations.
        pod_name (str): Name of the pod to search for.

    Returns:
        dict: Pod configuration if found, None otherwise.
    """
    for pod_config in pods_config:
        if pod_config['name'] == pod_name:
            return pod_config
    return None


# Function to get performance expectations associated with a given pod
def get_pod_cost(config_data,pod):
    pod_name=pod[1]
    pod_type=pod[2]	    
    pod_class=pod[3]
    initial_node=pod[4]
    pod_ran_delay=pod[5]
    
# Function to get pod configuration and namespace from loaded config
def get_pod_config(config_data,pod):
    
    pod_name=pod[1]
    pod_type=pod[2]	    
    pod_class=pod[3]
    initial_node=pod[4]
    pod_ran_delay=pod[5]
 
    pod_config = get_pod_config_by_type(config_data['pods_config'], pod_type)
    pod_transmission_data= pod_config["transmission_uplink"]+pod_config["transmission_downlink"]

    return {
        "name": pod_name,  # Name of the pod
        "CPU": pod_config["CPU"],    # CPU value in milli CPUs
        "RAM": pod_config["RAM"],    # RAM value in Mi
        "storage":pod_config["storage"],  # Storage in Mi
        "instructions":pod_config["instructions"],
        "namespace": config_data["namespace"],  # Namespace
        "pod_ran_delay":pod_ran_delay, # Pod communication delay
        "pod_class": pod_class, # Class of the pod : gu/bu/be
        "initial_node": initial_node, # Node receiving the request
        "namespace": config_data["namespace"], # Namespace for pod
        "pod_transmission_data": pod_transmission_data # Data that should be transmissed for this pod
        
    }
# Function to generate resource limits based on pod type
def generate_resources(pod_config):
    cpu = pod_config["CPU"]
    ram = pod_config["RAM"]

    if pod_config["pod_class"] == "guaranteed":
        return {
            "requests": {"cpu": f"{cpu}m",
                         "memory": f"{ram}Mi"},
            "limits": {"cpu": f"{cpu}m",  
                       "memory": f"{ram}Mi"}
        }
    elif pod_config["pod_class"]:
        return {
            "requests": {"cpu": f"{cpu//2}m",  # Half of limit for burstable
                         "memory": f"{ram//2}Mi"},
            "limits": {"cpu": f"{cpu}m",
                       "memory": f"{ram}Mi"}
        }
    else:  # Best-effort
        return {}
        
        
def get_pod_spec(config_data,running_node, pod_config):
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
    
    resources = generate_resources(pod_config)
    inter_node_delay= get_inter_node_delay(config_data,pod_config["initial_node"],running_node,pod_config["pod_transmission_data"])
    # Priority class could be useful is pods should be prioritized at execution (ie multiple queues), line below enables to retrieve information regarding priority class
    # priority_class = get_pod_priority_class(pod_type) 
    spec = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": pod_config["name"],
            "namespace": pod_config["namespace"],
            "annotations": {
                "transmission_delay": str(pod_config["pod_ran_delay"]),
                "initial_node": pod_config["initial_node"],
                "inter_node_delay" : str(inter_node_delay)
            }
        },
        "spec": {
            "nodeName": running_node,
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
def launch_pod(config_data,running_node, pod_config, api_instance):
    
    # Define pod specification
    pod_manifest = get_pod_spec(config_data,running_node, pod_config)
    
    # Create the pod
    api_instance.create_namespaced_pod(namespace=pod_config["namespace"], body=pod_manifest)
    pod_type=pod_config["pod_class"]
    print(f"Pod launched on node {running_node} with type: {pod_type}")
    
# Get the list of pods that are part of the Pods dataset and that belong to a specific interval of time
def get_interval_pods_lists(config_data,interval_min,interval_max):
    pods=load_dataset(config_data['pods_dataset_file'])
    matching_pods=[]
    for pod in pods:
        pod_data = pod.strip().split(',')
        pod_start_time=int(pod_data[0])
        if interval_min < pod_start_time <= interval_max:
            matching_pods.append(pod_data)
    return matching_pods



