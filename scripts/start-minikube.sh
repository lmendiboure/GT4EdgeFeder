#!/bin/bash


# Check if the argument is given
if [ $# -ne 1 ]; then
  echo "Usage: $0 <config_number> (2,3,4,5,6,8 currently available)"
  exit 1
fi

CONFIG_NUMBER=$1
CONFIG_FILE="../config/config-${CONFIG_NUMBER}.yaml"
TEMP_CONFIG_FILE="../config/temp-config.yaml"


# Check if file exists

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Error: File $CONFIG_FILE does not exist."
  exit 1
fi

# Crate a copy a the selected config file named "temp-config.yaml"
cp "$CONFIG_FILE" "$TEMP_CONFIG_FILE"

# Check if copy created
if [ $? -ne 0 ]; then
  echo "Error: Failed to create $TEMP_CONFIG_FILE."
  exit 1
fi

echo "Copied $CONFIG_FILE to $TEMP_CONFIG_FILE. Will be used during future experiments until new configuration selection."


# Load configuration from config.yaml
namespace=$(cat "$TEMP_CONFIG_FILE" | grep "namespace:" | awk '{print $2}')
disk_size=$(cat "$TEMP_CONFIG_FILE" | grep "disk_size:" | awk '{print $2}')
nodes_number=$(cat "$TEMP_CONFIG_FILE" | grep "nodes_number:" | awk '{print $2}')
memory=$(cat "$TEMP_CONFIG_FILE" | grep "memory:" | awk '{print $2}')
cpus=$(cat "$TEMP_CONFIG_FILE" | grep "cpus:" | awk '{print $2}')

# Start Minikube with specified disk size and nodes
minikube start --driver=docker --disk-size="$disk_size" --nodes="$nodes_number" --memory="$memory" --cpus="$cpus"

# Create namespace if it doesn't exist
kubectl get namespace "$namespace" >/dev/null 2>&1 || kubectl create namespace "$namespace"

# Add Metric Server; check if running: kubectl get pods --all-namespaces | grep metrics-server
minikube addons enable metrics-server


# Other potential fonctions

# Apply priority Class management => Prioritize Guaranteeed & Burstable VS Best-effort : Could be useful if multiple queues were used (ie potential use)
#kubectl apply -f ../config/priority_classes.yaml

# Apply disruption management : could be useful if multiple instances of a same service were running
#kubectl apply -f ../config/pod_disruption_budgets.yaml

# Apply components.yaml -> Alternative solution to Metric Server
#kubectl apply -f ../config/components.yaml
