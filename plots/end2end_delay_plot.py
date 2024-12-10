import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

####################################
#
#
# usage : python3 end2end_delay_plot.py results/8-12-18-25
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
	columns = ["timestamp", "pod", "event", "running_node_name", "origin_node", "transmission_delay", "inter_node_delay", "e2edelay"]
	df = pd.read_csv(file, sep=',', names=columns)

	# Filtrer les lignes où `event = "Succeeded"` et convertir `e2edelay` en numérique
	df['e2edelay'] = pd.to_numeric(df['e2edelay'], errors='coerce')  # Convertir les valeurs en nombres
	df_filtered = df[df['event'] == "Succeeded"]  # Filtrer pour event = "Succeeded"
	df_filtered = df_filtered.dropna(subset=['e2edelay'])  # Supprimer les lignes où e2edelay est NaN
	df_filtered['e2edelay']=df_filtered['e2edelay'].div(1000)

	# Mettre les données du fichier traité dans une structure globale
	if subdir[2:] not in dataframes:
		dataframes[subdir[2:]]=dict()
	dataframes[subdir[2:]][subdir[:1]]=df_filtered['e2edelay']

# Applanir la structure pour en faire un dataframe panda
rows = []
for group, subgroups in dataframes.items():
    for subgroup, series in subgroups.items():
        # Create a DataFrame for this specific series
        df = pd.DataFrame({
            'Group': group,
            'Subgroup': subgroup,
            'e2edelay': series.values
        })
        rows.append(df)

# Combine all rows into a single DataFrame
final_df = pd.concat(rows, ignore_index=True)

# Boxplot it
group_order = ['25-solo', '50-solo', '75-solo', '25-multi', '50-multi', '75-multi', "nous"]  # Order for the groups
subgroup_order = ['2', '4', '8'] 
plt.figure(figsize=(12, 6))
sns.boxplot(data=final_df, x='Group', y='e2edelay', hue='Subgroup', order=group_order, hue_order=subgroup_order, fill=False, showmeans=True,
            meanprops={"marker":"*",
                       "markerfacecolor":"red", 
                       "markeredgecolor":"red",
                      "markersize":"10"}  )
# Add a title
plt.title("Box Plot of Total Bill by Day and Smoker Status")

# Add labels to the axes
plt.xlabel("Orchestration Solutions")
plt.ylabel("time (s)")

# Save file à la racine
save_file=path+'e2edelay_grouped.pdf'
plt.savefig(save_file, format='pdf', dpi=300, bbox_inches='tight')
plt.close()


# Same operation but only fopr solo + nous
group_order = ['25-solo', '50-solo', '75-solo', "nous"]  # Order for the groups
subgroup_order = ['2', '4', '8'] 
plt.figure(figsize=(6, 6))
filtered_df = final_df[final_df['Group'].isin(['25-solo', '50-solo', '75-solo', "nous"])]

sns.boxplot(data=filtered_df, x='Group', y='e2edelay', hue='Subgroup', order=group_order, hue_order=subgroup_order, fill=False, showmeans=True,
            meanprops={"marker":"*",
                       "markerfacecolor":"red", 
                       "markeredgecolor":"red",
                      "markersize":"10"}  )
# Add a title
plt.title("Distribution of end-to-end delays in application processing request")
# Add labels to the axes
plt.xlabel("Orchestration Solutions")
plt.ylabel("time (s)")
# Save file à la racine
save_file=path+'e2edelay_solo_nous.pdf'
plt.savefig(save_file, format='pdf', dpi=300, bbox_inches='tight')
plt.close()


# Same operation but onbly for multi and nous
group_order = ['25-multi', '50-multi', '75-multi', "nous"]  # Order for the groups
subgroup_order = ['2', '4', '8'] 
plt.figure(figsize=(6, 6))
filtered_df = final_df[final_df['Group'].isin(['25-multi', '50-multi', '75-multi', "nous"])]

sns.boxplot(data=filtered_df, x='Group', y='e2edelay', hue='Subgroup', order=group_order, hue_order=subgroup_order, fill=False, showmeans=True,
            meanprops={"marker":"*",
                       "markerfacecolor":"red", 
                       "markeredgecolor":"red",
                      "markersize":"10"}  )
# Add a title
plt.title("Distribution of end-to-end delays in application processing request")
# Add labels to the axes
plt.xlabel("Orchestration Solutions")
plt.ylabel("time (s)")
# Save file à la racine
save_file=path+'e2edelay_multi_nous.pdf'
plt.savefig(save_file, format='pdf', dpi=300, bbox_inches='tight')
plt.close()