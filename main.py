#!/usr/bin/env python3

import threading
from functions.watcher import watch_nodes,watch_pods, warmup_watcher
import time
from functions.utils import delete_pods, clean_experiment_files, load_config, rename_results_files
from functions.nodes_manager import multi_parameter_cooperative_node_selector, multi_parameter_partial_selfish_node_selector, mono_parameter_partial_selfish_node_selector, run_experimentation
from functions.warmup import launch_warmup_pods_on_all_nodes
import random
import sys
import argparse

stop_event= threading.Event()

if __name__ == '__main__':

    config_data = load_config("config.yaml")


    parser = argparse.ArgumentParser(description="Run Kubernetes experiment multiple times.")
    parser.add_argument('num_experiments', type=int, help='Number of times to run the experiment')
    args = parser.parse_args()
    index=1
    
    for experiment_number in range(1, args.num_experiments + 1):
        
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
        nodes_watcher_thread = threading.Thread(target=watch_nodes, args=(stop_event,))
        nodes_watcher_thread.start()
    
        # Run a thread measuring pods nodes stats
        pods_watcher_thread = threading.Thread(target=watch_pods, args=(stop_event,))
        pods_watcher_thread.start()
    
        # Run experiment
        run_experiment_thread= threading.Thread(target=run_experimentation, args=(multi_parameter_cooperative_node_selector,stop_event,))
        run_experiment_thread.start()
    
        # Catch Stop Experiment Event from Pod Watcher
        while(1):
    	    time.sleep(1)
    	    if stop_event.is_set():
                nodes_watcher_thread.join()
                pods_watcher_thread.join()
                print("******Ending experiment******\n")
                print("******All pods have been processed. Experiment is finished. Data can be found within the results folder.******\n")
                # Clean pods
                print("******Cleaning experiment******\n")	
                print("-> Deleting pods of the experiment (if any)\n")	
                delete_pods()
                
                rename_results_files(experiment_number)
                
                if (index == args.num_experiments + 1):
                    sys.exit()
                else:
                    index+=1
                    stop_event.clear()
                    break
                 
