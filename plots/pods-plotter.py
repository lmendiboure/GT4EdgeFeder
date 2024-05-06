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
        node_names = {}  # Store node names for each pod
        transmission_delays = {} # Store transmission delays for each pod
        # Initialize dictionaries to store total times for each category and type
        total_pending_times = defaultdict(lambda: defaultdict(int))
        total_running_times = defaultdict(lambda: defaultdict(int))
        count_pending = defaultdict(lambda: defaultdict(int))
        count_running = defaultdict(lambda: defaultdict(int))
        # Iterate over each line in the file
        for line in file:
            # Split the line into timestamp, pod, event, and optionally node name
            parts = line.strip().split(',')
            timestamp_str, pod, event = parts[:3]
            node_name = parts[3] if len(parts) >= 4 else None
            transmission_delay = parts[4] if len(parts) > 4 else None
            # Convert the timestamp string to total milliseconds
            timestamp_ms = convert_to_milliseconds(timestamp_str)
            
            # Process the event
            if event == "Pending":
                # Store the pending time and node name for the pod
                if pod not in pending_times:
                    pending_times[pod] = timestamp_ms
                if node_name:
                    node_names[pod] = node_name
            elif event == "Running":
                # Store the running time and node name for the pod
                if pod not in running_times:
                    running_times[pod] = timestamp_ms
                if node_name:
                    node_names[pod] = node_name
                if transmission_delay:
                    transmission_delays[pod] = transmission_delay
            elif event == "Terminated":
                # Calculate the time differences if both pending and running times exist for the pod
                if pod in pending_times:
                    pending_time = pending_times.pop(pod)
                    time_difference_pending = timestamp_ms - pending_time
                    if time_difference_pending > 0:  # Check if time difference is positive
                        # Retrieve the node name for the pod
                        node_name = node_names.get(pod, "Unknown")
                        print(f"Pod {pod}: Time difference (Pending-Terminated) - {time_difference_pending} milliseconds")
                        category = pod.split('-pod-')[0]
                        pod_type = pod.split('-pod-')[1].split('-')[0]
                        total_pending_times[category][pod_type] += time_difference_pending
                        count_pending[category][pod_type] += 1
                if pod in running_times:
                    running_time = running_times.pop(pod)
                    time_difference_running = timestamp_ms - running_time
                    if time_difference_running > 0:  # Check if time difference is positive
                        # Retrieve the node name for the pod
                        node_name = node_names.get(pod, "Unknown")
                        transmission_delay = transmission_delays.get(pod, "Unknown")
                        print(f"Pod {pod}: Time difference (Running-Terminated) - {time_difference_running} milliseconds, Node Name - {node_name}, Transmission Delay - {transmission_delay}")
                        category = pod.split('-pod-')[0]
                        pod_type = pod.split('-pod-')[1].split('-')[0]
                        total_running_times[category][pod_type] += time_difference_running
                        count_running[category][pod_type] += 1
            else:
                # Remove the pod from pending and running times if it's not in "Pending" or "Running" state
                pending_times.pop(pod, None)
                running_times.pop(pod, None)
                node_names.pop(pod, None)

        # Calculate and print average times after processing all lines
        for category in total_pending_times:
            for pod_type in total_pending_times[category]:
                if count_pending[category][pod_type] > 0:
                    avg_pending_time = total_pending_times[category][pod_type] / count_pending[category][pod_type]
                    print(f"Category {category}, Type {pod_type}: Average Time difference (Pending-Terminated) - {avg_pending_time} milliseconds")
        # Probably not necessary. Pending-Terminated seems to better represent the time spent by a service in the system.
        #for category in total_running_times:
        #    for pod_type in total_running_times[category]:
        #        if count_running[category][pod_type] > 0:
        #            avg_running_time = total_running_times[category][pod_type] / count_running[category][pod_type]
        #            print(f"Category {category}, Type {pod_type}: Average Time difference (Running-Terminated) - {avg_running_time} milliseconds")


# Example usage
calculate_time_difference("./results/data_pods.csv")





