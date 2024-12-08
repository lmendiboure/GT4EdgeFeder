import os
import pandas as pd
import matplotlib.pyplot as plt

# Lire les données à partir du fichier CSV
data = pd.read_csv('data_nodes_experiment_1.csv', names=['Timestamp', 'Node', 'CPU', 'RAM', 'Storage'], skiprows=1)

# Convertir le timestamp en objet datetime
data['Timestamp'] = pd.to_datetime(data['Timestamp'])

# Trouver le timestamp initial (T0)
start_time = data['Timestamp'].min()

# Calculer le temps écoulé depuis T0 en secondes
data['TimeElapsed'] = (data['Timestamp'] - start_time).dt.total_seconds()


# Fonction pour afficher min, max et moyenne
def plot_statistique(data, stat_name, ylabel, title, file_name):
    stat_data = data.groupby('TimeElapsed').agg({stat_name: ['min', 'max', 'mean']})
    stat_data.columns = ['Min', 'Max', 'Mean']  # Renommer les colonnes pour plus de clarté

    # Plot des valeurs min, max et moyenne
    plt.figure(figsize=(10, 6))
    plt.plot(stat_data.index, stat_data['Min'], label='Min', linestyle='--')
    plt.plot(stat_data.index, stat_data['Max'], label='Max', linestyle='-.')
    plt.plot(stat_data.index, stat_data['Mean'], label='Mean', linestyle='-')

    plt.xlabel('Time (s)')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(file_name)  
    plt.close()

# Plot pourcentage d'utilisation de CPU
plot_statistique(data, 'CPU', 'CPU Usage (%)', 'Évolution de l\'utilisation CPU', './cpu_usage.pdf')

# Plot pourcentage d'utilisation de RAM
plot_statistique(data, 'RAM', 'RAM Usage (%)', 'Évolution de l\'utilisation RAM', './ram_usage.pdf')

# Plot pourcentage d'utilisation de stockage
plot_statistique(data, 'Storage', 'Storage Usage (%)', 'Évolution de l\'utilisation de Stockage', './storage_usage.pdf')
