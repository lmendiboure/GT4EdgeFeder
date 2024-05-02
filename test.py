import random

def get_random_latency_traffic(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        # Supprimer l'en-tête si nécessaire
        # lines = lines[1:]  # Décommentez cette ligne si la première ligne est un en-tête
        random_line = random.choice(lines)
        data = random_line.strip().split(',')
        traffic_load = int(data[11])
        latency = int(data[12])
        return latency, traffic_load

# Exemple d'utilisation :
#get_random_latency_traffic('5G_dataset_high_traffic_event.csv')
latency, traffic_load = get_random_latency_traffic('5G_dataset_high_traffic_event.csv')
print("Latence :", latency)
print("Charge de trafic :", traffic_load)
