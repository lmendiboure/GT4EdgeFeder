import pandas as pd
from datetime import datetime

def calculate_time_difference(file_path):
    """
    Calculate the time difference between the first "Running" event and the first "Terminated" event
    for each pod in the CSV file using Pandas.

    Args:
        file_path (str): Path to the CSV file containing pod events.

    Returns:
        None
    """
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path, names=["Timestamp", "Pod", "Event"])

    # Convert the Timestamp column to datetime objects
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    # Filter rows for "Running" and "Terminated" events
    running_df = df[df["Event"] == "Running"]
    terminated_df = df[df["Event"] == "Terminated"]

    # Group by Pod and find the first timestamp for each event type
    first_running_timestamps = running_df.groupby("Pod")["Timestamp"].first()
    first_terminated_timestamps = terminated_df.groupby("Pod")["Timestamp"].first()

    # Calculate time differences
    for pod in first_running_timestamps.index:
        if pod in first_terminated_timestamps:
            running_time = first_running_timestamps[pod]
            terminated_time = first_terminated_timestamps[pod]
            time_difference = terminated_time - running_time
            print(f"Pod {pod}: Time difference - {time_difference}")

# Example usage
calculate_time_difference("./results/data_pods.csv")

