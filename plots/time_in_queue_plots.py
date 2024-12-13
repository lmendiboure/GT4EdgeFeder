import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

####################################
#
#
# usage : python3 time_in_queue_plots.py results/8-12-18-25
#
#
####################################
path=sys.argv[1]
if path[-1] != '/':
	path+='/'
subdir_list=dict()
dataframes_grouped=dict()

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
	df['queuing_delay'] = pd.to_numeric(df['queuing_delay'], errors='coerce')  # Convertir les valeurs en nombres
	df_filtered = df[df['event'] == "Succeeded"]  # Filtrer pour event = "Succeeded"
	df_filtered = df_filtered.dropna(subset=['queuing_delay'])  # Supprimer les lignes où queuing_delay est NaN (je devrais pas en avoir normalement)

	# Mettre les données du fichier traité dans une structure globale
	# ATTENTION, dans cette proposition, nos boxplots sont au nombre de 3, i.e. 2, 4 et 8.
	if subdir[2:] not in dataframes_grouped:
		dataframes_grouped[subdir[2:]]=dict()
	dataframes_grouped[subdir[2:]][subdir[:1]]=df_filtered['queuing_delay']

# Applanir la structure pour en faire un dataframe panda
rows = []
for group, subgroups in dataframes_grouped.items():
    for subgroup, series in subgroups.items():
        # Create a DataFrame for this specific series
        df = pd.DataFrame({
            'Group': group,
            'Subgroup': subgroup,
            'queuing_delay': series.values
        })
        rows.append(df)

# Combine all rows into a single DataFrame
grouped_df = pd.concat(rows, ignore_index=True)

# Boxplot it
group_order = ['25-solo', '50-solo', '75-solo', '25-multi', '50-multi', '75-multi', "FaIRMEC"]  # Order for the groups
subgroup_order = ['2', '4', '8'] 
plt.figure(figsize=(6, 6))
sns.boxplot(data=grouped_df, x='Group', y='queuing_delay', hue='Subgroup', order=group_order, hue_order=subgroup_order, fill=False, showmeans=True,
            meanprops={"marker":"*",
                       "markerfacecolor":"red", 
                       "markeredgecolor":"red",
                      "markersize":"10"}  )
# Add a title
# plt.title("Time between users requests and responses")

# Add labels to the axes
plt.xlabel("Orchestration Solutions")
plt.ylabel("time (ms)")
plt.grid()
plt.show()
# Save file à la racine
save_file=path+'time_in_queue_grouped.pdf'
plt.savefig(save_file, format='pdf', dpi=300, bbox_inches='tight')
plt.close()


# debug(palette)
# # Same operation but only for 2 orchestrators
plt.figure(figsize=(6, 6))
sns.boxplot(data=grouped_df, x='Group', y='queuing_delay', hue='Subgroup', order=group_order, hue_order=subgroup_order[0], fill=False, showmeans=True,
            meanprops={"marker":"*",
                       "markerfacecolor":"red", 
                       "markeredgecolor":"red",
                      "markersize":"10"},color="seagreen" )
# Add labels to the axes
plt.xlabel("Orchestration Solutions")
plt.ylabel("time (ms)")
plt.grid()
# Save file à la racine
save_file=path+'time_in_queue_2_orchestrators.pdf'
plt.savefig(save_file, format='pdf', dpi=300, bbox_inches='tight')
# plt.close()

# # Same operation but only for 4 orchestrators
plt.figure(figsize=(6, 6))
sns.boxplot(data=grouped_df, x='Group', y='queuing_delay', hue='Subgroup', order=group_order, hue_order=subgroup_order[1], fill=False, showmeans=True,
            meanprops={"marker":"*",
                       "markerfacecolor":"red", 
                       "markeredgecolor":"red",
                      "markersize":"10"},color="seagreen"  )
# Add a title
# plt.title("Time between users requests and responses")

# Add labels to the axes
plt.xlabel("Orchestration Solutions")
plt.ylabel("time (ms)")
plt.grid()
# Save file à la racine
save_file=path+'time_in_queue_4_orchestrators.pdf'
plt.savefig(save_file, format='pdf', dpi=300, bbox_inches='tight')
plt.close()

# # Same operation but only for 8 orchestrators
plt.figure(figsize=(6, 6))
sns.boxplot(data=grouped_df, x='Group', y='queuing_delay', hue='Subgroup', order=group_order, hue_order=subgroup_order[2], fill=False, showmeans=True,
            meanprops={"marker":"*",
                       "markerfacecolor":"red", 
                       "markeredgecolor":"red",
                      "markersize":"10"},color="seagreen")
# Add a title
# plt.title("Time between users requests and responses")

# Add labels to the axes
plt.xlabel("Orchestration Solutions")
plt.ylabel("time (ms)")
plt.grid()
# Save file à la racine
save_file=path+'time_in_queue_4_orchestrators.pdf'
plt.savefig(save_file, format='pdf', dpi=300, bbox_inches='tight')
plt.close()