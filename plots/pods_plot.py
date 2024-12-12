import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

path=sys.argv[1]
if path[-1] != '/':
    path+='/'
file=path+'data_pods_experiment_1.csv'
output_file = path+"/boxplot_e2edelay.pdf"  # Nom du fichier de sortie

# Charger les données dans un DataFrame pandas
columns = ["timestamp", "pod", "event", "running_node_name", "origin_node", "transmission_delay", "inter_node_delay", "e2edelay", "queuing_delay", "waiting_number"]
df = pd.read_csv(file, sep=',', names=columns)

# Filtrer les lignes où `event = "Succeeded"` et convertir `e2edelay` en numérique
df['e2edelay'] = pd.to_numeric(df['e2edelay'], errors='coerce')  # Convertir les valeurs en nombres
df_filtered = df[df['event'] == "Succeeded"]  # Filtrer pour event = "Succeeded"
df_filtered = df_filtered.dropna(subset=['e2edelay'])  # Supprimer les lignes où e2edelay est NaN

# Calculer les statistiques pour tous les pods confondus
min_value = df_filtered['e2edelay'].min()
max_value = df_filtered['e2edelay'].max()
mean_value = df_filtered['e2edelay'].mean()

# Calculer le pourcentage de valeurs inférieures à 38000
threshold = 40000
percentage_below_threshold = (df_filtered['e2edelay'] < threshold).mean() * 100

# Calcul du pourcentage de pods réussis qui ne sont pas réalisés sur leur noeud d'origine
pods_non_origin_node = df_filtered[df_filtered['inter_node_delay'] != "0"]

percentage_non_origin_node = (len(pods_non_origin_node) / len(df_filtered)) * 100

# Calcul de la métrique `data_offload` si inter_node_delay est différent de 0
df_filtered['data_offload'] = 0  # Initialisation d'une nouvelle colonne 'data_offload'


# Logique pour ajouter la métrique data_offload en fonction du pod
for index, row in pods_non_origin_node.iterrows():
    if row['inter_node_delay'] != 0:  # Si inter_node_delay est différent de 0
        if 'julius' in row['pod']:
            df_filtered.at[index, 'data_offload'] = 160097 + 9032
        elif 'mrleo' in row['pod']:
            df_filtered.at[index, 'data_offload'] = 41000 * 2
        elif 'aeneas' in row['pod']:
            df_filtered.at[index, 'data_offload'] = 427347 + 816

# Calcul du total de data_offload
total_data_offload = df_filtered['data_offload'].sum()
percentage_offload = (total_data_offload / len(df_filtered))


# Afficher les statistiques dans le terminal
print("Statistiques des valeurs e2edelay (tous pods confondus, event = Succeeded):")
print(f"  Min : {min_value}")
print(f"  Max : {max_value}")
print(f"  Moyenne : {mean_value:.2f}\n")
print(f"  Satisfaction rate : {percentage_below_threshold:.2f}%\n")
print(f"  Pourcentage de pods offloadés: {percentage_non_origin_node:.2f}%\n")
print(f"  Total data offload : {total_data_offload}\n")
print(f"  Total data offload per task: {percentage_offload} \n")





# Générer un box plot global pour toutes les valeurs de e2edelay
plt.figure(figsize=(8, 6))
plt.boxplot(df_filtered['e2edelay'], vert=False, patch_artist=True)
plt.title("Box Plot des valeurs de e2edelay (tous pods confondus, event = Succeeded)")
plt.xlabel("e2edelay")
# Enregistrer la figure dans un fichier PDF

plt.savefig(output_file, format='pdf', dpi=300, bbox_inches='tight')  # Enregistrer avec une haute résolution
# print(f"Figure enregistrée sous : {output_file}")

plt.close()


