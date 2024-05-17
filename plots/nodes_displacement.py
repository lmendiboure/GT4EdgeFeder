import csv
from collections import defaultdict

def parse_csv(file_path):
    pod_data = {}
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            timestamp, pod, status, initial_node, transmission_delay, current_node = row
            category = pod.split('-pod-')[0]
            pod_type = pod.split('-pod-')[1].split('-')[0]
            pod_data[pod] = (timestamp, pod, status, initial_node, current_node, category, pod_type)
    return list(pod_data.values())

def calculate_displacement(pod_data):
    node_stats = defaultdict(lambda: defaultdict(lambda: {'total': 0, 'displaced': 0}))
    
    for timestamp, pod, status, initial_node, current_node, category, pod_type in pod_data:
        node_stats[initial_node][(category, pod_type)]['total'] += 1
        if initial_node != current_node:
            node_stats[initial_node][(category, pod_type)]['displaced'] += 1
    
    displacement_percentages = {}
    for initial_node, categories in node_stats.items():
        displacement_percentages[initial_node] = {}
        for (category, pod_type), stats in categories.items():
            total = stats['total']
            displaced = stats['displaced']
            percentage = (displaced / total) * 100 if total > 0 else 0
            displacement_percentages[initial_node][(category, pod_type)] = percentage
    
    return displacement_percentages

# Example usage
file_path = './results/data_pods.csv'
pod_data = parse_csv(file_path)
displacement_percentages = calculate_displacement(pod_data)

# Display the result
for node, categories in displacement_percentages.items():
    print(f'Node: {node}')
    for (category, pod_type), percentage in categories.items():
        print(f'  Category: {category}, Pod Type: {pod_type}, Displacement Percentage: {percentage:.2f}%')

