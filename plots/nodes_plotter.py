import os
import pandas as pd
import matplotlib.pyplot as plt

# Lire les données à partir du fichier CSV
data = pd.read_csv('./results/data_nodes.csv', names=['Timestamp', 'Node', 'CPU', 'RAM', 'Storage'], skiprows=1)

# Convertir le timestamp en objet datetime
data['Timestamp'] = pd.to_datetime(data['Timestamp'])

# Trouver le timestamp initial (T0)
start_time = data['Timestamp'].min()

# Calculer le temps écoulé depuis T0 en secondes
data['TimeElapsed'] = (data['Timestamp'] - start_time).dt.total_seconds()

# Créer le dossier "results" s'il n'existe pas déjà
if not os.path.exists('results'):
    os.makedirs('results')

# Plot pourcentage d'utilisation de CPU
plt.figure(figsize=(10, 6))
for node, group in data.groupby('Node'):
    plt.plot(group['TimeElapsed'], group['CPU'], label=node)

plt.xlabel('Time (s)')
plt.ylabel('CPU Usage (%)')
plt.title('Évolution de l\'utilisation CPU')
plt.legend()
plt.grid(True)
plt.savefig('results/cpu_usage.pdf')  # Enregistrer le plot dans le dossier "results"
plt.close()

# Plot pourcentage d'utilisation de RAM
plt.figure(figsize=(10, 6))
for node, group in data.groupby('Node'):
    plt.plot(group['TimeElapsed'], group['RAM'], label=node)

plt.xlabel('Time (s)')
plt.ylabel('RAM Usage (%)')
plt.title('Évolution de l\'utilisation RAM')
plt.legend()
plt.grid(True)
plt.savefig('results/ram_usage.pdf')  # Enregistrer le plot dans le dossier "results"
plt.close()

# Plot pourcentage d'utilisation de stockage
plt.figure(figsize=(10, 6))
for node, group in data.groupby('Node'):
    plt.plot(group['TimeElapsed'], group['Storage'], label=node)

plt.xlabel('Time (s)')
plt.ylabel('Storage Usage (%)')
plt.title('Évolution de l\'utilisation de Stockage')
plt.legend()
plt.grid(True)
plt.savefig('results/storage_usage.pdf')  # Enregistrer le plot dans le dossier "results"
plt.close()

# Calculer la somme normalisée pour chaque nœud
data['Total'] = (data['CPU'] + data['RAM'] + data['Storage']) / 3

# Plot pourcentage d'utilisation total
plt.figure(figsize=(10, 6))
for node, group in data.groupby('Node'):
    plt.plot(group['TimeElapsed'], group['Total'], label=node)

plt.xlabel('Time (s)')
plt.ylabel('Total Usage (%)')
plt.title('Évolution de l\'utilisation totale')
plt.legend()
plt.grid(True)
plt.savefig('results/total_usage.pdf')  # Enregistrer le plot dans le dossier "results"
plt.close()


