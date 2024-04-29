from datetime import datetime

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
    Calculate the time difference between the first "Pending" event and the first "Terminated" event
    for each pod in the CSV file without using Pandas.

    Args:
        file_path (str): Path to the CSV file containing pod events.

    Returns:
        None
    """
    # Open the CSV file
    with open(file_path, 'r') as file:
        # Initialize variables to store running and terminated times
        pending_times = {}  # Store pending times for each pod
        
        # Iterate over each line in the file
        for line in file:
            # Split the line into timestamp, pod, and event
            timestamp_str, pod, event = line.strip().split(',')
            
            # Convert the timestamp string to total milliseconds
            timestamp_ms = convert_to_milliseconds(timestamp_str)
            
            # Process the event
            if event == "Running":
                if pod not in pending_times:
                    pending_times[pod] = timestamp_ms
            elif event == "Terminated":
                if pod in pending_times:
                    pending_time = pending_times.pop(pod)
                    time_difference = timestamp_ms - pending_time
                    print(f"Pod {pod}: Time difference - {time_difference} milliseconds")

# Example usage
calculate_time_difference("./results/data_pods.csv")

