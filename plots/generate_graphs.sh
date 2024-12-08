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
   echo
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
# Instrument resources plotter
########################################################



for subdir in $(find "$directory" -mindepth 1 -maxdepth 1 -type d); do
    rm $subdir/{cpu_usage,ram_usage,storage_usage}.pdf $subdir/boxplot_e2edelay.pdf

    python3 nodes_plot.py $subdir
	if [ $? -eq 0 ]; then
	   echo "OK: Nodes plotting on $subdir OK."
	   python3 pods_plot.py $subdir
	   	if [ $? -eq 0 ]; then
	   		echo "OK: Pods plotting on $subdir OK."
	   	else
	   		echo "FAILED: Nodes plotting on $subdir error."
	   		exit
	   	fi
	else
		echo "FAILED: Nodes plotting on $subdir error."
		exit
	fi
    
done


