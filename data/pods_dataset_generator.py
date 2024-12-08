import random
import argparse
import math
import sys
sys.path.append('../functions')
from utils import load_config, write_to_csv, load_dataset, clean_csv     


# Function to generate random pod config from config file. We need to type on information: 1)pod name (ie application type) and 2) data to transmit to estimate transmission delays 

def generate_pod_config(config_data):
    random_app = random.choice(config_data['pods_config'])

    return {
        "name": random_app["name"],  # Name of the pod
        "transmission_uplink": random_app["transmission_uplink"], # Bits to transmit in Uplink
        "transmission_downlink": random_app["transmission_downlink"] # Bits to transmit in Downlink
    }

# Function to determine the latency associated with data transmission for a given pod. Based on data produced by measurements made in an EU project. Idea is to randomly select a measured value and compute transmission time based on the information related to a given Edge service.   
def get_ran_infos_for_pods(config_data,pod_config):
    lines=load_dataset(config_data['ran_dataset'])
    random_line = random.choice(lines[1:])
    data = random_line.strip().split(',')
    traffic_load = int(data[11])
    latency = int(data[12])
    print(latency)
    return math.ceil((pod_config["transmission_uplink"]+pod_config["transmission_downlink"])/(traffic_load*1000/(8*1000))+latency)

# Function to compute weights depending on the selected mode
def calculate_weights(nodes_number, mode):
    if mode == "uniform":
        # Tous les nœuds ont le même poids
        return [1 / nodes_number] * nodes_number
    elif mode == "mid_high":
        # 60% pour le premier nœud, 40% répartis équitablement entre les autres
        weights = [0.6] + [0.4 / (nodes_number - 1)] * (nodes_number - 1)
        return weights
    elif mode == "high":
        # 80% pour le premier nœud, 20% répartis équitablement entre les autres
        weights = [0.8] + [0.2 / (nodes_number - 1)] * (nodes_number - 1)
        return weights
    else:
        raise ValueError("Invalid mode. Choose 'uniform', 'mid_high', or 'high'.")
        
        
    
# Function to generate pods dataset for a specific duration and a variable number of pods
    
def generate_pods_dataset(mode):
    
    config_data = load_config("temp-config.yaml")

    random.seed(config_data["reproductible_seed"]) # Initialize PRNG for reproductibility purposes
    
    pod_counter = 1  # Initialize pod counter

    time=1 # Starting time of the experiment
    
    pods_dataset_file = config_data["pods_dataset_file"] # File used to store pods dataset

    clean_csv(pods_dataset_file) # Empty this file
    
    data = ["start_time", "name", "type", "class", "initial_name", "ran_delay"]
    
    write_to_csv(pods_dataset_file,data) # Add first line
    
    while (time<=config_data["expe_duration"]): # Generate pods all along the experimentation

        num_pods = random.randint(config_data["min_number_per_interval"], config_data["max_number_per_interval"]) # Random number of pods at each step
        
        for _ in range(num_pods):
            
            pod_config= generate_pod_config(config_data)
            
            pod_type = random.choice(["guaranteed", "burstable", "besteffort"]) # Random pod type selection
            
            pod_name = f"{pod_config['name']}-{pod_type[0]}{pod_type[1]}-{pod_counter}" # Unique pod name
            
            nodes_number = config_data["nodes_number"]
           
            weights = calculate_weights(nodes_number, mode)
            
            nodes = config_data["nodes_config"][:nodes_number]
           

            node_name = random.choices(population=[node["id"] for node in nodes], weights=weights, k=1)[0]
            
            print(node_name)
           
            #node_name = config_data["nodes_config"][(random.randint(0, config_data["nodes_number"]-1))]["id"] # Random node to attach pod
            
            ran_delay=get_ran_infos_for_pods(config_data,pod_config) # Compute transmission delay
            
            write_to_csv(pods_dataset_file, [time, pod_name, pod_config['name'], pod_type, node_name, ran_delay])

            # Increment pod counter for the next pod
            pod_counter += 1

            
        	
        time += config_data["pods_interval"]

if __name__ == "__main__":
    # Check argus
    parser = argparse.ArgumentParser(description="Indicate weighted probabilities.")
    parser.add_argument("mode", choices=["uniform", "mid_high", "high"], help="Weighting mode.")
    args = parser.parse_args()

    # generate dataset
    generate_pods_dataset(args.mode)





