import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

####################################
#
#
# usage : python3 data_offloaded_plot.py results/
#
#
####################################
path=sys.argv[1].split('/')[0]
if path[-1] != '/':
	path+='/'
subdir_list=dict()
dataframes=dict()
cnt_runs = 0

def debug(object):
	print(type(object))
	print(object)
	sys.exit(0)


for rundirs in os.listdir(path):
	if os.path.isfile(path+rundirs):
		continue
	subpath = path+rundirs + '/'
	# print(subpath)s
	for subdir in os.listdir(subpath):
		# print(subpath + subdir )
		# Discard files and process only directories
		if os.path.isfile(subpath+subdir):
			continue
		file=subpath+subdir+'/data_pods_experiment_1.csv'

		# Charger les données dans un DataFrame pandas
		columns = ["timestamp", "pod", "event", "running_node_name", "origin_node", "transmission_delay", "inter_node_delay", "e2edelay", "queuing_delay", "waiting_number"]
		df = pd.read_csv(file, sep=',', names=columns)

		# Filtrer les lignes où `event = "Succeeded"` et convertir `e2edelay` en numérique
		df['e2edelay'] = pd.to_numeric(df['e2edelay'], errors='coerce')  # Convertir les valeurs en nombres
		df_filtered = df[df['event'] == "Succeeded"]  # Filtrer pour event = "Succeeded"
		df_filtered = df_filtered.dropna(subset=['e2edelay'])  # Supprimer les lignes où e2edelay est NaN

		# Calcul du pourcentage de pods réussis qui ne sont pas réalisés sur leur noeud d'origine
		pods_non_origin_node = df_filtered[df_filtered['inter_node_delay'] != "0"]
		percentage_non_origin_node = (len(pods_non_origin_node) / len(df_filtered)) * 100
		# print(subpath+subdir)
		# print(percentage_non_origin_node)
		# Calcul de la métrique `data_offload` si inter_node_delay est différent de 0
		df_filtered['data_offload'] = 0  # Initialisation d'une nouvelle colonne 'data_offload'

		# # Logique pour ajouter la métrique data_offload en fonction du pod
		# for index, row in pods_non_origin_node.iterrows():
		#     if row['inter_node_delay'] != 0:  # Si inter_node_delay est différent de 0
		#         if 'julius' in row['pod']:
		#             df_filtered.at[index, 'data_offload'] = 160097 + 9032
		#         elif 'mrleo' in row['pod']:
		#             df_filtered.at[index, 'data_offload'] = 41000 * 2
		#         elif 'aeneas' in row['pod']:
		#             df_filtered.at[index, 'data_offload'] = 427347 + 816

		# # Calcul du total de data_offload
		# total_data_offload = df_filtered['data_offload'].sum()
		# percentage_offload = (total_data_offload / len(df_filtered))

		# Mettre données récupérées dans structure globale
		if subdir[2:] not in dataframes:
			dataframes[subdir[2:]] = dict()
		if subdir[:1] not in dataframes[subdir[2:]]:
			dataframes[subdir[2:]][subdir[:1]] = percentage_non_origin_node 
		else:
			dataframes[subdir[2:]][subdir[:1]] += percentage_non_origin_node # percentage_non_origin_node/total_data_offload
	cnt_runs+=1

# debug(dataframes)
for group, subgroups in dataframes.items():
	# print(group)
	for series in dataframes[group]:
		# print(series)
		# print(dataframes[group])
		dataframes[group][series] /= cnt_runs
# sys.exit(0)
# Desired order of keys (groups)
group_order = ['25-multi', '50-multi', '75-multi',  'FaIRMEC']
subgroup_order = ['2', '4', '8'] 
# Create DataFrame and reorder based on the desired order
# debug(dataframes)
plotting_data = pd.DataFrame(dataframes).transpose()
plotting_data = plotting_data.reindex(group_order)
plotting_data = plotting_data[subgroup_order]

# Plot it
plotting_data.plot(kind='bar', width=0.9, figsize=(6, 5), zorder = 3)
plt.xlabel("Orchestration Solutions", fontsize=12)
plt.ylabel("Applications offloaded (%)", fontsize=12)
plt.xticks(fontsize=12, rotation=45)
plt.yticks(fontsize=12)
plt.legend()
plt.legend(loc='upper left', bbox_to_anchor=(1.0, 0.5),title='#Orchestrators',title_fontsize='12', fontsize=12)
# Style it
plt.grid(zorder = 0)
plt.tight_layout()
sns.despine()
# Show or save it
# plt.show()
save_file=path+'percent_offloaded_average_multiruns.pdf'
plt.savefig(save_file, format='pdf', dpi=300, bbox_inches='tight')
plt.close()

# # Same ops but for compare against a subset
# group_order = ['25-solo','50-solo', '75-solo', 'nous']
# filtered_data = plotting_data.loc[group_order]
# filtered_data.plot(kind='bar', width=0.8, figsize=(6, 6), zorder = 3)
# # Layout formatting
# plt.legend(loc='upper left', bbox_to_anchor=(0.08, 1.0))
# plt.title("User satisfaction levels in application processing request")
# plt.xlabel("Orchestration Solutions")
# plt.ylabel("User satisfaction (%)")
# plt.grid(zorder = 0)
# # Show or save
# save_file=path+'satisfaction_rate_solo-nous.pdf'
# plt.savefig(save_file, format='pdf', dpi=300, bbox_inches='tight')
# plt.close()

# # # Same ops but for compare against a subset
# group_order = ['25-multi','50-multi', '75-multi', 'nous']
# filtered_data = plotting_data.loc[group_order]
# filtered_data.plot(kind='bar', width=0.8, figsize=(6, 6), zorder = 3)
# # Layout formatting
# plt.legend(loc='upper left', bbox_to_anchor=(0.08, 1.0))
# plt.title("User satisfaction levels in application processing request")
# plt.xlabel("Orchestration Solutions")
# plt.ylabel("User satisfaction (%)")
# plt.grid(zorder = 0)
# # Show or save
# save_file=path+'satisfaction_rate_multi-nous.pdf'
# plt.savefig(save_file, format='pdf', dpi=300, bbox_inches='tight')
# plt.close()