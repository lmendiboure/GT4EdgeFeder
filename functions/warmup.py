from kubernetes import client, config
from functions.utils import get_available_nodes
import random
import string

def generate_random_string(length=6):
    """Generate a random string of fixed length."""
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

def create_pod(api_instance, namespace, node_name, pod_template):
    """Create a pod on a specific node."""
    pod_name = f"warmup-pod-{generate_random_string()}"
    pod_template['metadata']['name'] = pod_name
    pod_template['spec']['nodeName'] = node_name

    # Create the pod
    api_instance.create_namespaced_pod(namespace=namespace, body=pod_template)
    print(f"Pod {pod_name} created on node {node_name}")

def get_pod_template():
    """Return a pod template as a Python dictionary."""
    return {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': 'warmup-pod'
        },
        'spec': {
            "restartPolicy": "Never",
            'containers': [{
                "name": "example-container",
                "image": "python:3.9",
                'resources': {
                    'requests': {
                        'cpu': '100m',
                        'memory': '100Mi'
                    },
                    'limits': {
                        'cpu': '200m',
                        'memory': '200Mi'
                    }
                }
            }]
        }
    }

def launch_warmup_pods_on_all_nodes(namespace):
    """Launch pods on all nodes for warmup."""
    # Load Kubernetes configuration
    config.load_kube_config()

    # Create a client to interact with the Kubernetes API
    api_instance = client.CoreV1Api()

    # Get the pod template
    pod_template = get_pod_template()

    # List all nodes in the cluster
    nodes = get_available_nodes(api_instance)
    
    for node_name in nodes:
        create_pod(api_instance, namespace, node_name, pod_template)
