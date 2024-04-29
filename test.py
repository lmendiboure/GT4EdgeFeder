import random
import threading
import time
import csv
from datetime import datetime
from kubernetes import client, config, watch

# Function to get the list of available nodes
def get_available_nodes():
    config.load_kube_config()
    api_instance = client.CoreV1Api()
    nodes = api_instance.list_node().items
    return [node.metadata.name for node in nodes]

# Function to launch a pod on a random node with a specified duration
def launch_pod(namespace, node_name, duration):
    config.load_kube_config()
    api_instance = client.CoreV1Api()

    # Define pod specification
    pod_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": f"example-pod-{random.randint(1, 1000)}",
            "namespace": namespace
        },
        "spec": {
            "nodeName": node_name,
            "restartPolicy": "Never",
            "containers": [
                {
                    "name": "example-container",
                    "image": "python:3.9",
                    "command": ["python", "-u", "-c",
                        "import math; primes = [num for num in range(2, 100000) if all(num % i != 0 for i in range(2, int(math.sqrt(num)) + 1))]"],
                    "resources": {
                        "requests": {
                            "memory": "64Mi",
                            "cpu": "100m"
                        }
                    }
                }
            ]
            }
        }

    # Create the pod
    api_instance.create_namespaced_pod(namespace=namespace, body=pod_manifest)
    print(f"Pod launched on node {node_name}")

# Function to watch pods in a namespace


def write_to_csv(filename, data):
    """
    Write data to a CSV file.

    Args:
        filename (str): Path to the CSV file.
        data (list): Data to be written to the CSV file.
    """
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)
        
        

def watch_pods(namespace):
    config.load_kube_config()
    api_instance = client.CoreV1Api()

    print("Watching pods...")

    w = watch.Watch()
    for event in w.stream(api_instance.list_namespaced_pod, namespace=namespace):
        pod_name = event['object'].metadata.name
        pod_phase = event['object'].status.phase
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if pod_phase == "Running":
            print(f"Pod {pod_name} is now Running.")
            write_to_csv("test.csv", [timestamp, pod_name, "Running"])

        elif pod_phase == "Failed" or pod_phase == "Succeeded":
            print(f"Pod {pod_name} status: {pod_phase}")
            write_to_csv("test.csv", [timestamp, pod_name, "Terminated"])

        elif pod_phase == "Pending":
            print(f"Pod {pod_name} is pending...")

        elif pod_phase == "Unknown":
            print(f"Pod {pod_name} status: Unknown")

        else:
            print(f"Pod {pod_name} status: {pod_phase}")
# Main function
def main():
    namespace = "expe"
    duration = 3

    # Start watching pods in a separate thread
    watch_thread = threading.Thread(target=watch_pods, args=(namespace,), daemon=True)
    watch_thread.start()

    # Get the list of available nodes
    available_nodes = get_available_nodes()

    # Launch pods periodically
    while True:
        node_name = random.choice(available_nodes)
        launch_pod(namespace, node_name, duration)
        time.sleep(random.randint(1, 3))

if __name__ == "__main__":
    main()
