#!/bin/bash

# Load configuration from config.yaml
namespace=$(cat ../config/config.yaml | grep "namespace:" | awk '{print $2}')
disk_size=$(cat ../config/config.yaml | grep "disk_size:" | awk '{print $2}')
nodes_number=$(cat ../config/config.yaml | grep "nodes_number:" | awk '{print $2}')
memory=$(cat ../config/config.yaml | grep "memory:" | awk '{print $2}')
cpus=$(cat ../config/config.yaml | grep "cpus:" | awk '{print $2}')

# Start Minikube with specified disk size and nodes
minikube start --disk-size="$disk_size" --nodes="$nodes_number" --memory="$memory" --cpus="$cpus"

# Create namespace if it doesn't exist
kubectl get namespace "$namespace" >/dev/null 2>&1 || kubectl create namespace "$namespace"

# Add Metric Server; check if running: kubectl get pods --all-namespaces | grep metrics-server
minikube addons enable metrics-server

# Apply priority Class management => Prioritize Guaranteeed & Burstable VS Best-effort
kubectl apply -f ../config/priority_classes.yaml

# Apply premption management : high priority pods could interrupt the operation of low priority pods
kubectl apply -f ../config/pod_disruption_budgets.yaml

# Apply components.yaml -> Alternative solution to Metric Server
#kubectl apply -f ../config/components.yaml
