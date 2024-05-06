import random
import time    
from functions.watcher import get_nodes_utilization
import os   

# Reproduces Multi-Parameter Game Theory Node selection 
def multi_parameter_gt_node_selector(available_nodes):
    storage_data, cpu_data, ram_data = get_nodes_utilization(output_file=None)
    lowest_load_node = None
    lowest_load = float('inf')  # Initialize with positive infinity
    for node in available_nodes:
        cpu_utilization_rate = cpu_data.get(node, 0)
        ram_utilization_rate = ram_data.get(node, 0)
        storage_utilization_rate = storage_data.get(node, 0)
        
        # Calculate cumulative load
        cumulative_load = (cpu_utilization_rate + ram_utilization_rate + storage_utilization_rate) / 3
        
        if cumulative_load < lowest_load:
            lowest_load = cumulative_load
            lowest_load_node = node
    return lowest_load_node
    
# Reproduces CPU Based Game Theory Node selection 
def cpu_gt_node_selector(available_nodes):
    storage_data, cpu_data, ram_data = get_nodes_utilization(output_file=None)
    lowest_load_node = None
    lowest_load = float('inf')  # Initialize with positive infinity    
    for node in available_nodes:
        cpu_utilization_rate = cpu_data.get(node, 0)
        if cpu_utilization_rate < lowest_load:
            lowest_load = cpu_utilization_rate
            lowest_load_node = node
    return lowest_load_node

    

# Random node selection => Simplest way to balance the load between nodes
def random_node_selector(available_nodes):
	return random.choice(available_nodes)

