import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

path=sys.argv[1]
if path[-1] != '/':
    path+='/'
file=path+'data_nodes_experiment_1.csv'
# Lire les données à partir du fichier CSV
data = pd.read_csv(file, names=['Timestamp', 'Node', 'CPU', 'RAM', 'Storage'], skiprows=1)

# Convertir le timestamp en objet datetime
data['Timestamp'] = pd.to_datetime(data['Timestamp'])

# Trouver le timestamp initial (T0)
start_time = data['Timestamp'].min()

# Calculer le temps écoulé depuis T0 en secondes
data['TimeElapsed'] = (data['Timestamp'] - start_time).dt.total_seconds()


# Fonction pour afficher min, max et moyenne
def plot_statistique(data, stat_name, ylabel, title, file_name):
    stat_data = data.groupby('TimeElapsed').agg({stat_name: ['min', 'max', 'mean']})
    stat_data.columns = ['min', 'max', 'mean']  # Renommer les colonnes pour plus de clarté

    # Plot des valeurs min, max et moyenne
    plt.figure(figsize=(10, 6))
    plt.plot(stat_data.index, stat_data['min'], label='Min', linestyle='--')
    plt.plot(stat_data.index, stat_data['max'], label='Max', linestyle='-.')
    plt.plot(stat_data.index, stat_data['mean'], label='Mean', linestyle='-')

    plt.xlabel('Time (s)')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(file_name)  
    plt.close()

# Plot pourcentage d'utilisation de CPU
plot_statistique(data, 'CPU', 'CPU Usage (%)', 'Évolution de l\'utilisation CPU', path+'/cpu_usage.pdf')

# Plot pourcentage d'utilisation de RAM
plot_statistique(data, 'RAM', 'RAM Usage (%)', 'Évolution de l\'utilisation RAM', path+'/ram_usage.pdf')

# Plot pourcentage d'utilisation de stockage
plot_statistique(data, 'Storage', 'Storage Usage (%)', 'Évolution de l\'utilisation de Stockage', path+'/storage_usage.pdf')
