import threading
from functions.watcher import watch_nodes,watch_pods
import time
from functions.podsgenerator import run_pods
from functions.utils import delete_pods
from functions.nodes_selector import multi_parameter_gt_node_selector, cpu_gt_node_selector, random_node_selector

if __name__ == '__main__':

    # Clean environment
    	
    delete_pods()
    
    # Run a thread measuring every second nodes nodes stats
    thread = threading.Thread(target=watch_nodes)
    thread.start()
    
    # Run a thread measuring pods nodes stats
    thread = threading.Thread(target=watch_pods)
    thread.start()
    
    run_pods(multi_parameter_gt_node_selector)
    
