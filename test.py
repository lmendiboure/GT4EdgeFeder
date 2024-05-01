from kubernetes import client, config
import time

def get_node_cpu_usage(node_name):
    config.load_kube_config()  # Charge la configuration Kubernetes depuis ~/.kube/config

    metric_api = client.CustomObjectsApi()

    try:
        metrics = metric_api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
        for item in metrics['items']:
            if item['metadata']['name'] == node_name:
                cpu_usage = item['usage']['cpu']
                return cpu_usage
    except Exception as e:
        print("Erreur lors de la récupération de l'utilisation du CPU du nœud :", e)
        return None

def get_node_cpu_capacity(node_name):
    config.load_kube_config()  # Charge la configuration Kubernetes depuis ~/.kube/config

    v1 = client.CoreV1Api()

    try:
        node = v1.read_node(node_name)
        cpu_capacity = node.status.capacity['cpu']
        return cpu_capacity
    except Exception as e:
        print("Erreur lors de la récupération de la capacité CPU du nœud :", e)
        return None

def parse_cpu_quantity(cpu_str):
    if cpu_str.endswith("n"):
        return int(cpu_str[:-1]) / 10**9
    else:
        return int(cpu_str)

def get_node_memory_usage(node_name):
    config.load_kube_config()  # Charge la configuration Kubernetes depuis ~/.kube/config

    metric_api = client.CustomObjectsApi()

    try:
        metrics = metric_api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
        for item in metrics['items']:
            if item['metadata']['name'] == node_name:
                memory_usage = item['usage']['memory']
                memory_usage_bytes = parse_memory_quantity(memory_usage)
                return memory_usage_bytes
    except Exception as e:
        print("Erreur lors de la récupération de l'utilisation de la mémoire du nœud :", e)
        return None

def get_node_memory_capacity(node_name):
    config.load_kube_config()  # Charge la configuration Kubernetes depuis ~/.kube/config

    v1 = client.CoreV1Api()

    try:
        node = v1.read_node(node_name)
        memory_capacity = node.status.capacity['memory']
        memory_capacity_bytes = parse_memory_quantity(memory_capacity)
        return memory_capacity_bytes
    except Exception as e:
        print("Erreur lors de la récupération de la capacité mémoire du nœud :", e)
        return None

def parse_memory_quantity(memory_str):
    if memory_str.endswith("Ki"):
        return int(memory_str[:-2]) * 1024
    elif memory_str.endswith("Mi"):
        return int(memory_str[:-2]) * 1024 * 1024
    elif memory_str.endswith("Gi"):
        return int(memory_str[:-2]) * 1024 * 1024 * 1024
    elif memory_str.endswith("Ti"):
        return int(memory_str[:-2]) * 1024 * 1024 * 1024 * 1024
    else:
        raise ValueError("Unité de mémoire non reconnue")

def main():
    node_names = ["minikube-m02", "minikube"]  # Remplacez par les noms réels de vos nœuds Kubernetes

    while True:
        for node_name in node_names:
            # CPU
            cpu_usage = get_node_cpu_usage(node_name)
            cpu_capacity = get_node_cpu_capacity(node_name)
            if cpu_usage is not None and cpu_capacity is not None:
                cpu_usage_cpu = parse_cpu_quantity(cpu_usage)
                cpu_capacity_cpu = parse_cpu_quantity(cpu_capacity)
                cpu_ratio = cpu_usage_cpu / float(cpu_capacity_cpu)
                print("Ratio d'utilisation du CPU sur le nœud {}: {:.2f}%".format(node_name, cpu_ratio * 100))
            else:
                print("Impossible de récupérer les métriques d'utilisation et de capacité du CPU.")

            # RAM
            memory_usage = get_node_memory_usage(node_name)
            memory_capacity = get_node_memory_capacity(node_name)
            if memory_usage is not None and memory_capacity is not None:
                memory_ratio = memory_usage / memory_capacity
                print("Ratio d'utilisation de la mémoire sur le nœud {}: {:.2f}%".format(node_name, memory_ratio * 100))
            else:
                print("Impossible de récupérer les métriques d'utilisation et de capacité de la mémoire.")

        time.sleep(1)  # Pause d'une seconde avant de récupérer les valeurs à nouveau

if __name__ == "__main__":
    main()

