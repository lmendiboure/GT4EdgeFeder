import threading
from functions.watcher import watch_nodes,watch_pods
import time
from functions.podsgenerator import run_pods
from functions.utils import delete_pods


if __name__ == '__main__':

    # Clean environment
    	
    #delete_pods()
    
    # Run a thread measuring every second nodes nodes stats
    thread = threading.Thread(target=watch_nodes)
    thread.start()
    
    # Run a thread measuring pods nodes stats
    thread = threading.Thread(target=watch_pods)
    thread.start()
    
    run_pods()
    
