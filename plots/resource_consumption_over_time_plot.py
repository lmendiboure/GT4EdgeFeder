import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

path=sys.argv[1]
if path[-1] != '/':
    path+='/'
file=path+'data_nodes_experiment_1.csv'
file_name = path + path.split('/')[-2] + '_conso_ALL_resources.pdf'
def debug(object):
    print(type(object))
    print(object)
    sys.exit(0)

# Lire les données à partir du fichier CSV
data = pd.read_csv(file, names=['Timestamp', 'Node', 'CPU', 'RAM', 'Storage'], skiprows=1)

# Convertir le timestamp en objet datetime
data['Timestamp'] = pd.to_datetime(data['Timestamp'])

# Trouver le timestamp initial (T0)
start_time = data['Timestamp'].min()

# Calculer le temps écoulé depuis T0 en secondes
data['TimeElapsed'] = (data['Timestamp'] - start_time).dt.total_seconds()

# Fonction pour afficher min, max et moyenne
def plot_statistique(data, stat_name):
    stat_data = data.groupby('TimeElapsed').agg({stat_name: ['min', 'max', 'mean']})
    # debug(stat_data)
    stat_data.columns = ['Min', 'Max', 'Mean']  # Renommer les colonnes pour plus de clarté

    if stat_name == 'CPU':
        color = 'red' 
        colorfill = 'crimson'
    elif stat_name == 'RAM':
        color = 'green' 
        colorfill = 'forestgreen'
    else:
        color = 'blue' 
        colorfill = 'dodgerblue'
    # Fill between min and max
    plt.fill_between(stat_data.index, stat_data['Min'], stat_data['Max'], color=colorfill, alpha=0.5, label='Min-Max '+stat_name)

    # Plot mean
    sns.lineplot(x='TimeElapsed', y='Mean', data=stat_data, color=color, label='Mean '+ stat_name)




# Plot des valeurs min, max et moyenne
plt.figure(figsize=(6, 6))
# Plot pourcentage d'utilisation de CPU
plot_statistique(data, 'CPU')

# Plot pourcentage d'utilisation de RAM
plot_statistique(data, 'RAM')

# Plot pourcentage d'utilisation de stockage
plot_statistique(data, 'Storage')

ylabel = 'Resources usage (%)'

plt.xlabel('Time (s)')
plt.ylabel(ylabel)
plt.ylim(0, 105) 

plt.legend()
plt.grid(True)
plt.savefig(file_name)  
# plt.show()