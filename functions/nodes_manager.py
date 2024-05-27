import random
import time    
from functions.watcher import get_nodes_utilization, stop_event
from functions.utils import load_config, convert_memory_usage_to_megabytes, parse_memory_string, write_to_csv, load_dataset, get_inter_node_delay, get_available_nodes, get_node_resources_infos, order_nodes_by_delay     
from functions.pods_manager import get_pod_config, launch_pod, get_interval_pods_lists 
from kubernetes import client, config, watch
import os   

    	

# Reproduces Multi-Parameter Game Theory Node selection 
def multi_parameter_gt_node_selector(waiting_pods,available_nodes,config_data,api_instance):
    
    storage_data, cpu_data, ram_data = get_nodes_utilization(config_data,output_file=None)
    node_list = {node: {} for node in available_nodes}

    # Initialize nodes infos: maximum load that can be achieved and current load
    for index, node in enumerate(available_nodes):
        max_cpu, max_ram, max_storage = get_node_resources_infos(config_data, index)
        node_list[node]["cpu_used"]= cpu_data.get(node, 0)*max_cpu
        node_list[node]["cpu_max"] = max_cpu
        node_list[node]["ram_used"] = ram_data.get(node, 0) * max_ram
        node_list[node]["ram_max"] = max_ram
        node_list[node]["storage_used"] = storage_data.get(node, 0) * max_storage
        node_list[node]["storage_max"] = max_storage
    
    for pod in waiting_pods:
        pod_config = get_pod_config(config_data,pod)
        initial_node= pod_config["initial_node"]
        pod_cpu=pod_config["CPU"]
        pod_ram=pod_config["RAM"]
        pod_storage= pod_config["storage"]
        
        potential_node= random.choice(available_nodes)

        # Check if initial node is able to manage this pod
        if ((node_list[initial_node]["cpu_used"] + pod_cpu/1000) < node_list[initial_node]["cpu_max"] and (node_list[initial_node]["ram_used"] + pod_ram) < node_list[initial_node]["ram_max"] and (node_list[initial_node]["storage_used"] + pod_storage) < node_list[initial_node]["storage_max"]):
            node_list[initial_node]["cpu_used"] += pod_cpu/1000
            node_list[initial_node]["ram_used"] += pod_ram
            node_list[initial_node]["storage_used"] += pod_storage
            running_node = initial_node
            launch_pod(config_data,running_node, pod_config, api_instance)
            waiting_pods.remove(pod)        
            
        # Check if other nodes are able to manage this pod 
           
        else:
            for dest_node in order_nodes_by_delay(config_data,initial_node):
                if ((node_list[dest_node]["cpu_used"] + pod_cpu/1000) < node_list[dest_node]["cpu_max"] and (node_list[dest_node]["ram_used"] + pod_ram) < node_list[dest_node]["ram_max"] and (node_list[dest_node]["storage_used"] + pod_storage) < node_list[dest_node]["storage_max"]):
                    node_list[dest_node]["cpu_used"] += pod_cpu/1000
                    node_list[dest_node]["ram_used"] += pod_ram
                    node_list[dest_node]["storage_used"] += pod_storage
                    running_node = dest_node
                    launch_pod(config_data,running_node, pod_config, api_instance)
                    waiting_pods.remove(pod) 
                    break
         
    return waiting_pods
    
# Reproduces CPU Based Game Theory Node selection 
def cpu_gt_node_selector(available_nodes):
    storage_data, cpu_data, ram_data = get_nodes_utilization(config_data,output_file=None)
    node_list = {node: {} for node in available_nodes}

    # Initialize nodes infos: maximum load that can be achieved and current load
    for index, node in enumerate(available_nodes):
        max_cpu, max_ram, max_storage = get_node_resources_infos(config_data, index)
        node_list[node]["cpu_used"]= cpu_data.get(node, 0)*max_cpu
        node_list[node]["cpu_max"] = max_cpu
    
    for pod in waiting_pods:
        pod_config = get_pod_config(config_data,pod)
        initial_node= pod_config["initial_node"]
        pod_cpu=pod_config["CPU"]
        
        # Check if initial node is able to manage this pod
        if ((node_list[initial_node]["cpu_used"] + pod_cpu/1000) < node_list[initial_node]["cpu_max"]):
            node_list[initial_node]["cpu_used"] += pod_cpu/1000
            node_list[initial_node]["ram_used"] += pod_ram
            node_list[initial_node]["storage_used"] += pod_storage
            running_node = initial_node
            launch_pod(config_data,running_node, pod_config, api_instance)
            waiting_pods.remove(pod)        
            
        # Check if other pods are able to manage this pod 
           
        else:
            for dest_node in order_nodes_by_delay(config_data,initial_node):
                if ((node_list[initial_node]["cpu_used"] + pod_cpu/1000) < node_list[initial_node]["cpu_max"]):
                    node_list[initial_node]["cpu_used"] += pod_cpu/1000
                    node_list[initial_node]["ram_used"] += pod_ram
                    node_list[initial_node]["storage_used"] += pod_storage
                    running_node = initial_node
                    launch_pod(config_data,running_node, pod_config, api_instance)
                    waiting_pods.remove(pod) 
                    break
         
    return waiting_pods



# Dynamic Selfish node selection => Services are placed only if resources are sufficient

def dynamic_selfish_node_selector(waiting_pods,available_nodes,config_data,api_instance):

    storage_data, cpu_data, ram_data = get_nodes_utilization(config_data,output_file=None)
    node_list = {node: {} for node in available_nodes}

    # Initialize nodes infos: maximum load that can be achieved and current load
    for index, node in enumerate(available_nodes):
        max_cpu, max_ram, max_storage = get_node_resources_infos(config_data, index)
        node_list[node]["cpu_used"]= cpu_data.get(node, 0)*max_cpu
        node_list[node]["cpu_max"] = max_cpu
        node_list[node]["ram_used"] = ram_data.get(node, 0) * max_ram
        node_list[node]["ram_max"] = max_ram
        node_list[node]["storage_used"] = storage_data.get(node, 0) * max_storage
        node_list[node]["storage_max"] = max_storage
    
    for pod in waiting_pods:
        pod_config = get_pod_config(config_data,pod)
        initial_node= pod_config["initial_node"]
        pod_cpu=pod_config["CPU"]
        pod_ram=pod_config["RAM"]
        pod_storage= pod_config["storage"]
        
        
        # Check if initial node is able to manage this pod
        if ((node_list[initial_node]["cpu_used"] + pod_cpu/1000) < node_list[initial_node]["cpu_max"] and (node_list[initial_node]["ram_used"] + pod_ram) < node_list[initial_node]["ram_max"] and (node_list[initial_node]["storage_used"] + pod_storage) < node_list[initial_node]["storage_max"]):
            node_list[initial_node]["cpu_used"] += pod_cpu/1000
            node_list[initial_node]["ram_used"] += pod_ram
            node_list[initial_node]["storage_used"] += pod_storage
            running_node = initial_node
            launch_pod(config_data,running_node, pod_config, api_instance)
            waiting_pods.remove(pod)        
         
    return waiting_pods


# Selfish node selection => Opposite to a Federation process: Tasks are not exchanged between nodes
def selfish_node_selector(waiting_pods,available_nodes,config_data,api_instance):

    for pod in waiting_pods:
        pod_config = get_pod_config(config_data,pod)
        initial_node= pod_config["initial_node"]
        launch_pod(config_data,initial_node, pod_config, api_instance)
        waiting_pods.remove(pod)

    return waiting_pods


# Sort pods by priority
def custom_sort_key(item):
    priority = {'guaranteed': 0, 'burstable': 1, 'besteffort': 2}
    return priority[item[3]]

# Function to run experimentation based on a predetermined set of pods
def run_experimentation(node_selection_func):

    config_data = load_config("config.yaml")
    
    current_time= 0
    game_interval = config_data["game_interval"]

    config.load_kube_config()
    api_instance = client.CoreV1Api()

    # Get the list of available nodes
    available_nodes = get_available_nodes(api_instance)
    
    # Define a list of pods what will be used all along the experiment    
    waiting_pods=[]

    # Run experimentation based on elapsed time
    
    while not stop_event.is_set():
    
        # Wait for a game interval
        time.sleep(config_data["game_interval"])
	
	# Add pods corresponding to the current time slot
        if (current_time<=config_data["expe_duration"]):
            new_pods=get_interval_pods_lists(config_data, current_time, current_time+game_interval)

        waiting_pods.extend(new_pods)

        # Sort waiting pods list by priority

        waiting_pods=sorted(waiting_pods, key=custom_sort_key)

        if waiting_pods:
            waiting_pods=node_selection_func(waiting_pods, available_nodes,config_data,api_instance)
        current_time+=config_data["game_interval"]
