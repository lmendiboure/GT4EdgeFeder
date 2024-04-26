import threading
from functions.functions import get_storage_and_resource_utilization_for_all_nodes,watch_nodes,watch_pods
import time


if __name__ == '__main__':

    # Run a thread measuring every second nodes nodes stats
    thread = threading.Thread(target=watch_nodes)
    thread.start()
    
    # Run a thread measuring pods nodes stats
    thread = threading.Thread(target=watch_pods)
    thread.start()

