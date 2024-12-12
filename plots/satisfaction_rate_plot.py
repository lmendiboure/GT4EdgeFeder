import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

####################################
#
#
# usage : python3 satisfaction_rate_plot.py results/8-12-18-25
#
#
####################################
path=sys.argv[1]
if path[-1] != '/':
	path+='/'
subdir_list=dict()
dataframes=dict()

def debug(object):
	print(type(object))
	print(object)
	sys.exit(0)

for subdir in os.listdir(path):

	# Discard files and process only directories
	if os.path.isfile(path+subdir):
		continue
	file=path+subdir+'/data_pods_experiment_1.csv'

	# Charger les données dans un DataFrame pandas
	columns = ["timestamp", "pod", "event", "running_node_name", "origin_node", "transmission_delay", "inter_node_delay", "e2edelay", "queuing_delay", "waiting_number"]
	df = pd.read_csv(file, sep=',', names=columns)

	# Filtrer les lignes où `event = "Succeeded"` et convertir `e2edelay` en numérique
	df['e2edelay'] = pd.to_numeric(df['e2edelay'], errors='coerce')  # Convertir les valeurs en nombres
	df_filtered = df[df['event'] == "Succeeded"]  # Filtrer pour event = "Succeeded"
	df_filtered = df_filtered.dropna(subset=['e2edelay'])  # Supprimer les lignes où e2edelay est NaN

	# Calculer le pourcentage de valeurs inférieures à 38000
	threshold = 40000
	percentage_below_threshold = (df_filtered['e2edelay'] < threshold).mean() * 100

	# Mettre les données du fichier traité dans une structure globale
	if subdir[2:] not in dataframes:
		dataframes[subdir[2:]] = dict()
	dataframes[subdir[2:]][subdir[:1]] = percentage_below_threshold
# debug(dataframes)
# Create Figure
# group_order = ['25-solo', '50-solo', '75-solo', '25-multi', '50-multi', '75-multi', "nous"]  # Order for the groups
# subgroup_order = ['2', '4', '8'] 
# plt.figure(figsize=(12, 6))
# sns.barplot(data = dataframes,x=group_order, hue=subgroup_order, order=group_order, hue_order=subgroup_order)
# plt.show()

# Desired order of keys (groups)
group_order = ['25-solo','50-solo', '75-solo', '25-multi', '50-multi', '75-multi',  'nous']
subgroup_order = ['2', '4', '8'] 
# Create DataFrame and reorder based on the desired order
plotting_data = pd.DataFrame(dataframes).transpose()
plotting_data = plotting_data.reindex(group_order)
plotting_data = plotting_data[subgroup_order]
# Plot it
plotting_data.plot(kind='bar', width=0.8, figsize=(6, 6), zorder = 3)
# Layout formatting
# plt.tight_layout()
plt.legend(loc='upper left', bbox_to_anchor=(0.08, 1.0))
plt.title("User satisfaction levels in application processing request")
plt.xlabel("Orchestration Solutions")
plt.ylabel("User satisfaction (%)")
plt.grid(zorder = 0)
# Show or save
# plt.show()
# sys.exit(0)
save_file=path+'satisfaction_rate_grouped.pdf'
plt.savefig(save_file, format='pdf', dpi=300, bbox_inches='tight')
plt.close()

# Same ops but for compare against a subset
group_order = ['25-solo','50-solo', '75-solo', 'nous']
filtered_data = plotting_data.loc[group_order]
filtered_data.plot(kind='bar', width=0.8, figsize=(6, 6), zorder = 3)
# Layout formatting
plt.legend(loc='upper left', bbox_to_anchor=(0.08, 1.0))
plt.title("User satisfaction levels in application processing request")
plt.xlabel("Orchestration Solutions")
plt.ylabel("User satisfaction (%)")
plt.grid(zorder = 0)
# Show or save
save_file=path+'satisfaction_rate_solo-nous.pdf'
plt.savefig(save_file, format='pdf', dpi=300, bbox_inches='tight')
plt.close()

# # Same ops but for compare against a subset
group_order = ['25-multi','50-multi', '75-multi', 'nous']
filtered_data = plotting_data.loc[group_order]
filtered_data.plot(kind='bar', width=0.8, figsize=(6, 6), zorder = 3)
# Layout formatting
plt.legend(loc='upper left', bbox_to_anchor=(0.08, 1.0))
plt.title("User satisfaction levels in application processing request")
plt.xlabel("Orchestration Solutions")
plt.ylabel("User satisfaction (%)")
plt.grid(zorder = 0)
# Show or save
save_file=path+'satisfaction_rate_multi-nous.pdf'
plt.savefig(save_file, format='pdf', dpi=300, bbox_inches='tight')
plt.close()