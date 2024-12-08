import time
import sys
from kubernetes import client, config, watch
from datetime import datetime
from functions.utils import load_config, convert_memory_usage_to_megabytes, parse_memory_string, write_to_csv, compute_pods_number, get_available_nodes, get_node_resources_infos
import random
import threading
from datetime import datetime


def watch_pods(stop_event):
    """
    Watch pods in a specified namespace and log their phase transitions to a CSV file. Sends a "Stop Experiment" event when all pods have been processed (ie. number of pods completed is equal to the number of pods in the experiment file.
    """
    try: 

        # Load configuration data from the YAML file
        config_data = load_config("temp-config.yaml")
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
        
            arrival_time = event['object'].metadata.annotations['arrival_time']
            
            # Get current timestamp with milliseconds
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            # Check the phase of the pod and take appropriate action
            if pod_phase == "Pending":
                print(f"Pod {pod_name} is now Pending.")
                #write_to_csv(results_file_pods, [timestamp, pod_name, "Pending", running_node, initial_node, transmission_delay, inter_node_delay,""])

            elif pod_phase == "Running":
                # Write timestamp, pod name, and phase to the CSV file
                print(f"Pod {pod_name} is now Running on Node {running_node}. Transmission delay is equal to {transmission_delay}. Inter node delay is equal to {inter_node_delay}")
                #write_to_csv(results_file_pods, [timestamp, pod_name, "Running", running_node, initial_node, transmission_delay, inter_node_delay,""])
		
            elif pod_phase == "Succeeded":
                print(f"Pod {pod_name} is now Completed.")
                # Write timestamp, pod name, and phase to the CSV file
                current_timestamp = datetime.now().isoformat()
                # Value specifically used for succeeded status: E2E time
                elapsed_time = int((datetime.fromisoformat(current_timestamp) - datetime.fromisoformat(arrival_time)).total_seconds() * 1000)  # Convert to milliseconds
                write_to_csv(results_file_pods, [timestamp, pod_name, "Succeeded", running_node, initial_node, transmission_delay, inter_node_delay,elapsed_time])
                processed_pods_number+=1
                if processed_pods_number==expe_pods_number:
                    processed_pods_number = 0
                    stop_event.set()
                    break
            # So far only get the info for failed pods.         
            elif pod_phase == "Failed": 
                print(f"Pod {pod_name} has Failed.")
                write_to_csv(results_file_pods, [timestamp, pod_name, "Failed", running_node, initial_node, transmission_delay, inter_node_delay,""])
                processed_pods_number+=1
                if processed_pods_number==expe_pods_number:
                    processed_pods_number = 0
                    stop_event.set()
                    break
    
    except Exception as e:
        # Handle any exceptions and print error message
        print(f"Error watching pods:", e)



def warmup_watcher():
    """
    Watch a specific number of pods. Aims to verify that experimentations can properly work on the considered machine. Also aims to avoid potential network issues at experimentation start.
    """
    try: 

        # Load configuration data from the YAML file
        config_data = load_config("temp-config.yaml")
        # Get the namespace from the configuration data
        namespace = config_data['namespace']
                
        processed_pods_number = 0
         	
        # Load Kubernetes configuration from default location
        config.load_kube_config()
        
        # Create a client to interact with the Kubernetes API
        api_instance = client.CoreV1Api()

        # Get nodes number
        nodes = get_available_nodes(api_instance)
        pods_number = len(nodes)

        # Initialize a watch stream
        w = watch.Watch()

        # Iterate over events in the watch stream
        for event in w.stream(api_instance.list_namespaced_pod, namespace=namespace):
            # Extract pod name and phase from the event
            pod_name = event['object'].metadata.name
            pod_phase = event['object'].status.phase
            running_node = event['object'].spec.node_name  
            
            if pod_phase == "Succeeded":
                print(f"Pod {pod_name} is now Completed on node {running_node}.")
                processed_pods_number+=1
                if processed_pods_number==pods_number:
                    break
            
            # So far only get the info for failed pods.         
            elif pod_phase == "Failed": 
                print(f"Pod {pod_name} has Failed on node {running_node}.")
                raise Exception("Error while running warm up phase. Please try again.")
    
    except Exception as e:
        # Handle any exceptions and print error message
        print(f"Error watching pods:", e)


def get_cluster_node_usage(api_instance, config_data):
    """Get the ephemeral storage usage for all nodes in the Kubernetes cluster."""
    try:
	# Retrieve infos from config file
        namespace = config_data['namespace']

        storage_data = {}
        cpu_data = {}
        ram_data = {}
        nodes = api_instance.list_node().items
        # Compute usage for each node
        for index, node in enumerate(nodes):
            # Get Node Info
            node_name = node.metadata.name
            node_cpu, node_ram, node_storage= get_node_resources_infos(config_data, index)

            # Store load values
            total_storage_used = 0
            total_cpu_used = 0
            total_ram_used = 0

            pods = api_instance.list_namespaced_pod(namespace=namespace, field_selector=f"spec.nodeName={node_name}").items
	    # Get pods infos to determine the used resources
            for pod in pods:
                if pod.status.phase == "Running" or pod.status.phase == "Pending":
                    for pod_config in config_data.get('pods_config', []):
                        if pod.metadata.name.startswith(pod_config['name']):
                            pod_storage_usage = pod_config['storage']
                            total_storage_used += pod_storage_usage
                            if "bu" in pod.metadata.name:
                                # Kubernetes, allocates a variable amount for burstable between Max/2 and Max
                                pod_cpu_usage = pod_config['CPU']
                                total_cpu_used += pod_cpu_usage/1000
                                pod_ram_usage = pod_config['RAM']
                                total_ram_used += pod_ram_usage    
                            elif "gu" in pod.metadata.name:
                                pod_cpu_usage = pod_config['CPU']
                                total_cpu_used += pod_cpu_usage/1000
                                pod_ram_usage = pod_config['RAM']
                                total_ram_used += pod_ram_usage   
                            elif "be" in pod.metadata.name:
                                # Kubernetes, allocates a variable amount for best effort between Max/4 and Max
                                pod_cpu_usage = pod_config['CPU']
                                total_cpu_used += pod_cpu_usage/1000
                                pod_ram_usage = pod_config['RAM']
                                total_ram_used += pod_ram_usage    
                            
	    # Store data for each node (With Minikube, load levels can rise to around 105%, so we minimise to display 100 at max.)	
            storage_data[node_name] = min((total_storage_used/node_storage)*100,100)
            cpu_data[node_name] = min((total_cpu_used/node_cpu)*100,100)
            ram_data[node_name] = min((total_ram_used/node_ram)*100,100)
            
        return storage_data, cpu_data, ram_data

    except Exception as e:
        print(f"Error retrieving cluster node usage information:", e)
        return None


def get_nodes_utilization(config_data,output_file=None):
    """Get CPU, RAM, and ephemeral storage utilization for all nodes in the Kubernetes cluster."""
    try:
        
        config.load_kube_config()  
                
        api_instance = client.CoreV1Api()
        
        nodes = api_instance.list_node().items
        # Compute usage
        storage_data, cpu_data, ram_data = get_cluster_node_usage(api_instance, config_data)
       
        if output_file:
            timestamp = datetime.now()
            for node in nodes:
                # Retrieve and store infos
                node_name = node.metadata.name
                cpu_utilization_rate = cpu_data.get(node_name, 0)
                ram_utilization_rate = ram_data.get(node_name, 0)
                storage_utilization_rate = storage_data.get(node_name, 0)
                write_to_csv(output_file, (timestamp, node_name, cpu_utilization_rate, ram_utilization_rate, storage_utilization_rate))
        return storage_data, cpu_data, ram_data
    except Exception as e:
        print(f"Error getting node utilization:", e)

    
    
def watch_nodes(stop_event):
    """
    Get nodes data for a specific namespace.Complete data result file every second.
    """
    config_data = load_config("temp-config.yaml")
    results_file_nodes = config_data.get('results_file_nodes', 'data.csv') 
        
    while not stop_event.is_set():
        storage_data, cpu_data, ram_data = get_nodes_utilization(config_data,output_file=results_file_nodes)
        print(f"Storage:{storage_data}, CPU:{cpu_data}, RAM:{ram_data}")
        time.sleep(0.5)
