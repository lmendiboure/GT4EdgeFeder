import time
import sys
from kubernetes import client, config, watch
from datetime import datetime
from functions.utils import load_config, convert_memory_usage_to_megabytes, parse_memory_string, write_to_csv, compute_pods_number    
import random
import threading

    
stop_event= threading.Event()

def watch_pods():
    """
    Watch pods in a specified namespace and log their phase transitions to a CSV file. Sends a "Stop Experiment" event when all pods have been processed (ie. number of pods completed is equal to the number of pods in the experiment file.
    """
    try: 

        # Load configuration data from the YAML file
        config_data = load_config("config.yaml")
        # Get the namespace from the configuration data
        namespace = config_data['namespace']
        
        expe_pods_number = compute_pods_number(config_data["pods_dataset_file"])
        
        processed_pods_number = 0
        
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
            running_node = event['object'].spec.node_name  # Get the node name
            transmission_delay = event['object'].metadata.annotations['transmission_delay']
            initial_node = event['object'].metadata.annotations['initial_node']
            inter_node_delay = event['object'].metadata.annotations['inter_node_delay']
            
            # Get current timestamp with milliseconds
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            # Check the phase of the pod and take appropriate action
            if pod_phase == "Pending":
                print(f"Pod {pod_name} is now Pending.")
                write_to_csv(results_file_pods, [timestamp, pod_name, "Pending", running_node, initial_node, transmission_delay, inter_node_delay])

            elif pod_phase == "Running":
                # Write timestamp, pod name, and phase to the CSV file
                print(f"Pod {pod_name} is now Running on Node {running_node}. Transmission delay is equal to {transmission_delay}. Inter node delay is equal to {inter_node_delay}")
                write_to_csv(results_file_pods, [timestamp, pod_name, "Running", running_node, initial_node, transmission_delay, inter_node_delay])
		
            elif pod_phase == "Succeeded":
                print(f"Pod {pod_name} is now Completed.")
                # Write timestamp, pod name, and phase to the CSV file
                write_to_csv(results_file_pods, [timestamp, pod_name, "Succeeded", running_node, initial_node, transmission_delay, inter_node_delay])
                processed_pods_number+=1
                if processed_pods_number==expe_pods_number:
                    stop_event.set()
                    break
            # So far only get the info for failed pods.         
            elif pod_phase == "Failed": 
                print(f"Pod {pod_name} has Failed.")
                processed_pods_number+=1
                if processed_pods_number==expe_pods_number:
                    stop_event.set()
                    break
    
    except Exception as e:
        # Handle any exceptions and print error message
        print(f"Error watching pods:", e)


def get_cluster_node_usage(api_instance, config_data):
    """Get the ephemeral storage usage for all nodes in the Kubernetes cluster."""
    try:
	# Retrieve infos from config file
        namespace = config_data['namespace']
        
        disk_size = config_data['disk_size']
        
        nodes_number = config_data['nodes_number']
        
        available_cpu = config_data['cpus']*nodes_number
        
        available_ram = config_data['memory']*nodes_number
        
        storage_size = disk_size 

        storage_data = {}
        cpu_data = {}
        ram_data = {}

        nodes = api_instance.list_node().items
        # Compute usage for each node
        for index, node in enumerate(nodes):
            # Get Node Info
            node_name = node.metadata.name
            node_cpu = available_cpu*config_data['nodes_config'][index]['CPU_percentage']
            node_ram=available_ram*config_data['nodes_config'][index]['RAM_percentage']
            node_storage= storage_size*config_data['nodes_config'][index]['storage_percentage']

            # Store load values
            total_storage_used = 0
            total_cpu_used = 0
            total_ram_used = 0

            pods = api_instance.list_namespaced_pod(namespace=namespace, field_selector=f"spec.nodeName={node_name}").items
	    # Get pods infos to determine the used resources
            for pod in pods:
                if pod.status.phase == "Running":
                    for pod_config in config_data.get('pods_config', []):
                        if pod.metadata.name.startswith(pod_config['name']):
                            pod_storage_usage = pod_config['storage']
                            total_storage_used += pod_storage_usage
                            if "bu" in pod.metadata.name:
                                pod_cpu_usage = random.randint(pod_config['CPU']/2, pod_config['CPU'])
                                total_cpu_used += pod_cpu_usage/1000
                                pod_ram_usage = random.randint(pod_config['RAM']/2, pod_config['RAM'])
                                total_ram_used += pod_ram_usage/10    
                            elif "gu" in pod.metadata.name:
                                pod_cpu_usage = pod_config['CPU']
                                total_cpu_used += pod_cpu_usage//1000
                                pod_ram_usage = pod_config['RAM']
                                total_ram_used += pod_ram_usage/10   
                            elif "be" in pod.metadata.name:
                                pod_cpu_usage = random.randint(0, pod_config['CPU'])
                                total_cpu_used += pod_cpu_usage/1000
                                pod_ram_usage = random.randint(0, pod_config['RAM'])
                                total_ram_used += pod_ram_usage/10    
                            
	    # Store data for each node	
            storage_data[node_name] = (total_storage_used/node_storage)*100
            cpu_data[node_name] = (total_cpu_used/node_cpu)*100
            ram_data[node_name] = (total_ram_used/node_ram)*100

        return storage_data, cpu_data, ram_data

    except Exception as e:
        print(f"Error retrieving ephemeral storage utilization information:", e)
        return None


def get_nodes_utilization(config_data,output_file=None):
    """Get CPU, RAM, and ephemeral storage utilization for all nodes in the Kubernetes cluster."""
    try:
        
        config.load_kube_config()  
                
        api_instance = client.CoreV1Api()
        
        nodes = api_instance.list_node().items
        # Compute usage
        storage_data, cpu_data, ram_data = get_cluster_node_usage(api_instance, config_data)
        print(f"Storage:{storage_data}, CPU:{cpu_data}, RAM:{ram_data}")
        timestamp = datetime.now()
       
        if output_file is None:
            return storage_data, cpu_data, ram_data
        
        else: 
            for node in nodes:
                # Retrieve and store infos
                node_name = node.metadata.name
                cpu_utilization_rate = cpu_data.get(node_name, 0)
                ram_utilization_rate = ram_data.get(node_name, 0)
                storage_utilization_rate = storage_data.get(node_name, 0)
                write_to_csv(output_file, (timestamp, node_name, cpu_utilization_rate, ram_utilization_rate, storage_utilization_rate))

    except Exception as e:
        print(f"Error retrieving resource utilization and storage information:", e)

    
    
def watch_nodes():
    """
    Get nodes data for a specific namespace.Complete data result file every second.
    """
    config_data = load_config("config.yaml")
    results_file_nodes = config_data.get('results_file_nodes', 'data.csv') 
        
    while not stop_event.is_set():
        get_nodes_utilization(config_data,output_file=results_file_nodes)
        time.sleep(1)
