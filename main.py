#!/usr/bin/env python3

import threading
from functions.watcher import watch_nodes,watch_pods, stop_event, warmup_watcher
import time
from functions.utils import delete_pods, clean_experiment_files, load_config
from functions.nodes_manager import multi_parameter_gt_node_selector, cpu_gt_node_selector, dynamic_selfish_node_selector, selfish_node_selector, run_experimentation
from functions.warmup import launch_warmup_pods_on_all_nodes
import random
import sys

if __name__ == '__main__':

    config_data = load_config("config.yaml")
    
    # Clean environment
    print("******Cleaning previous experiments******\n")	
    print("-> Deleting pods remaining from previous experiment (if any)\n")	
    delete_pods()
    print("Done.\n")
    print("-> Empty results files remaining from previous experiment (if any)\n")	
    clean_experiment_files()
    print("Done.\n")
    
    # Running warmup phase
    print("******Warm Up Phase******\n")	
    print("-> Initiating a pod on each node\n")	
    launch_warmup_pods_on_all_nodes(config_data['namespace'])
    print("\nDone.\n")
    print("-> Check that pods are completed properly. Could take a few seconds/minutes if images need to be pulled.\n")	
    warmup_watcher()
    print("\n-> Delete these pods.\n")
    delete_pods()
    print("Done.\n")
    
    # Running new experiment
    print("******Starting new experiment******\n")

    # Initialize randomness sequences
 
    random.seed(config_data["reproductible_seed"]) # Initialize PRNG for reproductibility purposes
    
    # Run a thread measuring every second nodes nodes stats
    nodes_watcher_thread = threading.Thread(target=watch_nodes)
    nodes_watcher_thread.start()
    
    # Run a thread measuring pods nodes stats
    pods_watcher_thread = threading.Thread(target=watch_pods)
    pods_watcher_thread.start()
    
    # Run experiment
    run_experiment_thread= threading.Thread(target=run_experimentation, args=(multi_parameter_gt_node_selector,))
    run_experiment_thread.start()
    
    # Catch Stop Experiment Event from Pod Watcher
    while(1):
    	time.sleep(1)
    	if stop_event.is_set():
            print("******Ending experiment******\n")
            print("******All pods have been processed. Experiment is finished. Data can be found within the results folder.******\n")
            # Clean pods
            print("******Cleaning experiment******\n")	
            print("-> Deleting pods of the experiment (if any)\n")	
            delete_pods()
            sys.exit() 
