from datetime import datetime
from collections import defaultdict

def convert_to_milliseconds(timestamp_str):
    """
    Convert a timestamp string containing seconds.milliseconds to total milliseconds.

    Args:
        timestamp_str (str): Timestamp string in the format "YYYY-MM-DD HH:MM:SS.mmm".

    Returns:
        int: Total milliseconds.
    """
    # Convert the timestamp string to a datetime object
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
    
    # Extract seconds and milliseconds from the datetime object
    seconds = timestamp.second
    milliseconds = timestamp.microsecond // 1000
    
    # Calculate total milliseconds
    total_milliseconds = seconds * 1000 + milliseconds
    
    return total_milliseconds

def calculate_time_difference(file_path):
    """
    Calculate two time differences:
    1) Between the first "Pending" and "Terminated" events for each pod.
    2) Between the first "Running" and "Terminated" events for each pod.
    Calculate the average duration for each category and type of pods after processing all pods.

    Args:
        file_path (str): Path to the CSV file containing pod events.

    Returns:
        None
    """
    # Open the CSV file
    with open(file_path, 'r') as file:
        # Initialize variables to store pending, running, and terminated times
        pending_times = {}  # Store pending times for each pod
        running_times = {}  # Store running times for each pod
        running_node_names = {}  # Store node names for each pod
        transmission_delays = {} # Store transmission delays for each pod
        inter_node_delays = {} # Store transmission delays for each pod
        # Initialize dictionaries to store total times for each category and type
        total_pending_times = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        count_pending = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))        
        total_end_to_end_times =  defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        # Iterate over each line in the file
        
        print("\nPrinting per pod results\n")
        # Skip the first line
        next(file)
        for line in file:
            # Split the line into timestamp, pod, event, and optionally node name
            parts = line.strip().split(',')
            timestamp_str, pod, event, running_node_name, origin_node, transmission_delay, inter_node_delay = parts

            # Convert the timestamp string to total milliseconds
            timestamp_ms = convert_to_milliseconds(timestamp_str)
            
            # Process the event
            if event == "Pending":
                # Store the pending time and node name for the pod
                if pod not in pending_times:
                    pending_times[pod] = timestamp_ms
                    running_node_names[pod] = running_node_name
                    transmission_delays[pod] = transmission_delay
                    inter_node_delays[pod]= inter_node_delay
            elif event == "Running":
                # Store the running time and node name for the pod
                if pod not in running_times:
                    running_times[pod] = timestamp_ms
                    running_node_names[pod] = running_node_name
                    transmission_delays[pod] = transmission_delay
                    inter_node_delays[pod]= inter_node_delay
            elif event == "Succeeded":
                # Calculate the time differences if both pending and running times exist for the pod
                if pod in pending_times:
                    pending_time = pending_times.pop(pod)
                    time_difference_pending = timestamp_ms - pending_time
                    if time_difference_pending > 0:  # Check if time difference is positive
                        # Retrieve the node name for the pod
                        running_node_name = running_node_names.get(pod, "Unknown")
                        transmission_delay = transmission_delays.get(pod, "Unknown")
                        inter_node_delay = inter_node_delays.get(pod,"Unknown")
                        print(f"Pod {pod}: Time difference (Pending-Succeeded) - {time_difference_pending} milliseconds, Node Name - {running_node_name}, Transmission Delay - {transmission_delay}, Inter Node Delay - {inter_node_delay}")
                        category = pod.split('-pod-')[0]
                        pod_type = pod.split('-pod-')[1].split('-')[0]
                        total_pending_times[category][pod_type][running_node_name] += time_difference_pending
                        total_end_to_end_times[category][pod_type][running_node_name] += time_difference_pending + int(transmission_delay) + int(inter_node_delay)
                        count_pending[category][pod_type][running_node_name] += 1

            else:
                # Remove the pod from pending and running times if it's not in "Pending" or "Running" state
                pending_times.pop(pod, None)
                node_names.pop(pod, None)

        # Calculate and print average times after processing all lines
        print("\nPrinting Results for Pods Categories/type:\n")
        for category in total_pending_times:
            for pod_type in total_pending_times[category]:
                for running_node_name in total_pending_times[category][pod_type]:
                    if count_pending[category][pod_type][running_node_name] > 0:
                        print(f"Category {category}, Type {pod_type}, Node {running_node_name}:") 
                        avg_pending_time = total_pending_times[category][pod_type][running_node_name] / count_pending[category][pod_type][running_node_name]
                        print(f"Average Time difference (Pending-Succeeded) - {avg_pending_time} milliseconds")
                        avg_end_to_end_time = total_end_to_end_times[category][pod_type][running_node_name] / count_pending[category][pod_type][running_node_name]
                        print(f"Average Time difference (End-to-end) - {avg_end_to_end_time} milliseconds\n")
# Example usage
calculate_time_difference("./results/data_pods_experiment_1.csv")





