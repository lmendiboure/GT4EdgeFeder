#! /bin/bash

unset -v directory


############################################################
# Help                                                     #
############################################################
Help()
{
   # Display Help
   echo "Bash script to instrument python tools to generate graphs."
   echo
   echo "Syntax: generate_graphs [-h|-d]"
   echo "options:"
   echo "-h         Print this Help."
   echo "-d <directory> 	Enter directory path where dataset results are located."
   echo "exemple usage : ./generate_graphs -d results/8-12-18-25"
}


###########################################################
while getopts ":hd:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      d) # specified results directory
      	directory=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done


shift "$(( OPTIND - 1 ))"

if [ -z "$directory" ] ; then
        echo 'Missing -d necessary argument' >&2
        exit 1
fi



########################################################
# Instrument resources plotter for each scenario
########################################################



for subdir in $(find "$directory" -mindepth 1 -maxdepth 1 -type d); do
    rm $subdir/{cpu_usage,ram_usage,storage_usage}.pdf $subdir/boxplot_e2edelay.pdf

    python3 nodes_plot.py $subdir
	if [ $? -eq 0 ]; then
	   echo "OK: Nodes plotted on $subdir OK."
	   python3 pods_plot.py $subdir
	   	if [ $? -eq 0 ]; then
	   		echo "OK: Pods plotted on $subdir OK."
            python3 resource_consumption_over_time_plot.py $subdir
               if [ $? -eq 0 ]; then
                  echo "OK: Resources plotted on $subdir OK."
               else
                  echo "FAILED: Resources plotting on $subdir error."
                  exit
               fi
	   	else
	   		echo "FAILED: Nodes plotting on $subdir error."
	   		exit
	   	fi
	else
		echo "FAILED: Nodes plotting on $subdir error."
		exit
	fi
    
done

########################################################
# Instrument graph tools at Federation Level
########################################################

# End-to-end delays 3 boxplots
echo "PLOTTING: End-to-end delay graphs"
python3 end2end_delay_plot.py $directory
echo "SUCCESS: End-to-end delay graphs"

# Network Traffic Bargraphs
echo "PLOTTING: Network Traffic graphs"
python3 data_offloaded_plot.py $directory
echo "SUCCESS: Network Traffic graphs"

# Time to process (queue + traitement) boxplots
echo "PLOTTING: Requests processing time graphs"
python3 time_to_process_plot.py $directory
echo "SUCCESS: Requests processing time graphs"

# Percentage of user satisfaction bargraphs
echo "PLOTTING: Users levels of satisfaction graphs"
python3 satisfaction_rate_plot.py $directory
echo "SUCCESS: Users levels of satisfaction graphs"