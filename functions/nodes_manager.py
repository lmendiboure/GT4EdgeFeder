import random
import time    
from functions.watcher import get_nodes_utilization
from functions.utils import load_config, convert_memory_usage_to_megabytes, parse_memory_string, write_to_csv, load_dataset, get_inter_node_delay, get_available_nodes, get_node_resources_infos, order_nodes_by_delay, get_processing_delay, get_selfish_ratio     
from functions.pods_manager import get_pod_config, launch_pod, get_interval_pods_lists 
from kubernetes import client, config, watch
from datetime import datetime

import os   

 
 # Reproduces the proposed solution with a multi-parameter approach (RAM, CPU, Storage). 
def multi_parameter_cooperative_node_selector(waiting_pods,available_nodes,config_data,api_instance):
    storage_data, cpu_data, ram_data = get_nodes_utilization(config_data,output_file=None)
    node_list = {node: {} for node in available_nodes}

    # Initialize nodes infos: maximum load that can be achieved and current load
    for index, node in enumerate(available_nodes):
        max_cpu, max_ram, max_storage = get_node_resources_infos(config_data, index)
        node_list[node]["cpu_used"]= cpu_data.get(node, 0)/100*max_cpu
        node_list[node]["cpu_max"] = max_cpu
        node_list[node]["ram_used"] = ram_data.get(node, 0)/100 * max_ram
        node_list[node]["ram_max"] = max_ram
        node_list[node]["storage_used"] = storage_data.get(node, 0)/100 * max_storage
        node_list[node]["storage_max"] = max_storage

    for pod in waiting_pods:
        pod_config = get_pod_config(config_data,pod)
        initial_node= pod_config["initial_node"]
        pod_cpu=pod_config["CPU"]
        pod_ram=pod_config["RAM"]
        pod_storage= pod_config["storage"]
        pod_arrival_time = pod[6]

        # Check which node is the most appropriate based on the game and place the pod
        for potential_node in order_nodes_by_delay(config_data, node_list, initial_node, pod_config["pod_transmission_data"],pod[2],pod_config["pod_class"]):
            if ((node_list[potential_node]["cpu_used"] + pod_cpu/1000) < node_list[potential_node]["cpu_max"] and (node_list[potential_node]["ram_used"] + pod_ram) < node_list[potential_node]["ram_max"] and (node_list[potential_node]["storage_used"] + pod_storage) < node_list[potential_node]["storage_max"]):
                node_list[potential_node]["cpu_used"] += pod_cpu/1000
                node_list[potential_node]["ram_used"] += pod_ram
                node_list[potential_node]["storage_used"] += pod_storage
                running_node = potential_node
                launch_pod(config_data,running_node, pod_config, api_instance,pod_arrival_time)
                waiting_pods.remove(pod) 
                break
         
    return waiting_pods
    	

# Reproduces the competitor solution with a multi-parameter approach (RAM, CPU, Storage). 
def multi_parameter_partial_selfish_node_selector(waiting_pods,available_nodes,config_data,api_instance):
    storage_data, cpu_data, ram_data = get_nodes_utilization(config_data,output_file=None)
    node_list = {node: {} for node in available_nodes}

    # Initialize nodes infos: maximum load that can be achieved and current load
    for index, node in enumerate(available_nodes):
        max_cpu, max_ram, max_storage = get_node_resources_infos(config_data, index)
        node_list[node]["cpu_used"]= cpu_data.get(node, 0)/100*max_cpu
        node_list[node]["cpu_max"] = max_cpu
        node_list[node]["ram_used"] = ram_data.get(node, 0)/100 * max_ram
        node_list[node]["ram_max"] = max_ram
        node_list[node]["storage_used"] = storage_data.get(node, 0)/100 * max_storage
        node_list[node]["storage_max"] = max_storage
        node_list[node]["selfish_ratio"] = get_selfish_ratio(config_data,node)
    for pod in waiting_pods:
        pod_config = get_pod_config(config_data,pod)
        initial_node= pod_config["initial_node"]
        pod_cpu=pod_config["CPU"]
        pod_ram=pod_config["RAM"]
        pod_storage= pod_config["storage"]
        pod_arrival_time = pod[6]
        # Check if initial node is able to manage this pod base on its selfish ratio
        
        if ((node_list[initial_node]["cpu_used"] + pod_cpu/1000) < (node_list[initial_node]["selfish_ratio"] * node_list[initial_node]["cpu_max"]) and (node_list[initial_node]["ram_used"] + pod_ram) < (node_list[initial_node]["selfish_ratio"] * node_list[initial_node]["ram_max"]) and (node_list[initial_node]["storage_used"] + pod_storage) < (node_list[initial_node]["selfish_ratio"] * node_list[initial_node]["storage_max"])):
            
            node_list[initial_node]["cpu_used"] += pod_cpu/1000
            node_list[initial_node]["ram_used"] += pod_ram
            node_list[initial_node]["storage_used"] += pod_storage
            running_node = initial_node
            launch_pod(config_data,running_node, pod_config, api_instance,pod_arrival_time)
            waiting_pods.remove(pod)        
            
        # Else check if other nodes are able to manage this pod 
        
        else:
            for dest_node in order_nodes_by_delay(config_data, node_list, initial_node, pod_config["pod_transmission_data"],pod[2],pod_config["pod_class"], include_initial_node=False):
                if ((node_list[dest_node]["cpu_used"] + pod_cpu/1000) < (1-node_list[dest_node]["selfish_ratio"]) *node_list[dest_node]["cpu_max"] and (node_list[dest_node]["ram_used"] + pod_ram) < (1-node_list[dest_node]["selfish_ratio"]) *node_list[dest_node]["ram_max"] and (node_list[dest_node]["storage_used"] + pod_storage) < (1-node_list[dest_node]["selfish_ratio"]) *node_list[dest_node]["storage_max"]):
                    node_list[dest_node]["cpu_used"] += pod_cpu/1000
                    node_list[dest_node]["ram_used"] += pod_ram
                    node_list[dest_node]["storage_used"] += pod_storage
                    running_node = dest_node
                    launch_pod(config_data,running_node, pod_config, api_instance,pod_arrival_time)
                    waiting_pods.remove(pod) 
                    break
         
    return waiting_pods
    
# Reproduces the operation of the competitor solution with a single parameter: CPU

def mono_parameter_partial_selfish_node_selector(waiting_pods,available_nodes,config_data,api_instance):
    storage_data, cpu_data, ram_data = get_nodes_utilization(config_data,output_file=None)
    node_list = {node: {} for node in available_nodes}

    # Initialize nodes infos: maximum load that can be achieved and current load
    for index, node in enumerate(available_nodes):
        max_cpu, max_ram, max_storage = get_node_resources_infos(config_data, index)
        node_list[node]["cpu_used"]= cpu_data.get(node, 0)/100*max_cpu
        node_list[node]["cpu_max"] = max_cpu
        node_list[node]["storage_used"] = storage_data.get(node, 0)/100 * max_storage
        node_list[node]["storage_max"] = max_storage
        node_list[node]["selfish_ratio"] = get_selfish_ratio(config_data,node)
    for pod in waiting_pods:
        pod_config = get_pod_config(config_data,pod)
        initial_node= pod_config["initial_node"]
        pod_cpu=pod_config["CPU"]
        pod_ram=pod_config["RAM"]
        pod_storage= pod_config["storage"]
        pod_arrival_time = pod[6]
        # Check if initial node is able to manage this pod base on its selfish ratio
        
        if ((node_list[initial_node]["cpu_used"] + pod_cpu/1000) < (node_list[initial_node]["selfish_ratio"] * node_list[initial_node]["cpu_max"])):
            
            node_list[initial_node]["cpu_used"] += pod_cpu/1000
            running_node = initial_node
            launch_pod(config_data,running_node, pod_config, api_instance,pod_arrival_time)
            waiting_pods.remove(pod)        
            
        # Else check if other nodes are able to manage this pod depending on their own selfishness
        
        else:
            for dest_node in order_nodes_by_delay(config_data, node_list, initial_node, pod_config["pod_transmission_data"],pod[2],pod_config["pod_class"], include_initial_node=False):
                if ((node_list[dest_node]["cpu_used"] + pod_cpu/1000) < (1-node_list[dest_node]["selfish_ratio"])*node_list[dest_node]["cpu_max"]):
                    node_list[dest_node]["cpu_used"] += pod_cpu/1000
                    running_node = dest_node
                    launch_pod(config_data,running_node, pod_config, api_instance,pod_arrival_time)
                    waiting_pods.remove(pod) 
                    break
         
    return waiting_pods


# Sort pods by priority
def custom_sort_key(item):
    priority = {'guaranteed': 0, 'burstable': 1, 'besteffort': 2}
    return priority[item[3]]

# Function to run experimentation based on a predetermined set of pods
def run_experimentation(node_selection_func,stop_event):

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
            # Sort new pods list by priority
            for pod in new_pods:
                current_timestamp = datetime.now().isoformat()
                pod.append(current_timestamp)
            new_pods_sorted = sorted(new_pods, key=custom_sort_key)

	# Add these pods in the waiting list
        waiting_pods.extend(new_pods)

        if waiting_pods:
            waiting_pods=node_selection_func(waiting_pods, available_nodes,config_data,api_instance)
        current_time+=config_data["game_interval"]
