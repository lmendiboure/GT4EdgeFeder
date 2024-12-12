import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

####################################
#
#
# usage : python3 cpu_global_conso_plot.py results/8-12-18-25
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
	file=path+subdir+'/data_nodes_experiment_1.csv'
	print(file)
	data = pd.read_csv(file, names=['Timestamp', 'Node', 'CPU', 'RAM', 'Storage'], skiprows=1)

	# In case we need to convert to numerals
	# df['CPU'] = pd.to_numeric(df['CPU'], errors='coerce')
	if subdir[2:] not in dataframes:
		dataframes[subdir[2:]]=dict()
	dataframes[subdir[2:]][subdir[:1]] = data['CPU']
	# dataframes[subdir[2:]][subdir[:1]] += data['RAM']
	# dataframes[subdir[2:]][subdir[:1]] += data['Storage']
	# debug(dataframes)
# Applanir la structure pour en faire un dataframe panda
rows = []
for group, subgroups in dataframes.items():
    for subgroup, series in subgroups.items():
        # Create a DataFrame for this specific series
        df = pd.DataFrame({
            'Group': group,
            'Subgroup': subgroup,
            'CPU': series.values
        })
        rows.append(df)

# Combine all rows into a single DataFrame
final_df = pd.concat(rows, ignore_index=True)

# Boxplot it
group_order = ['25-solo', '50-solo', '75-solo', '25-multi', '50-multi', '75-multi', "nous"]  # Order for the groups
subgroup_order = ['2', '4', '8'] 
plt.figure(figsize=(12, 6))
sns.boxplot(data=final_df, x='Group', y='CPU', hue='Subgroup', order=group_order, hue_order=subgroup_order, fill=False, showmeans=True,
            showfliers=False,meanprops={"marker":"*",
                       "markerfacecolor":"red", 
                       "markeredgecolor":"red",
                      "markersize":"10"}  )
# Add a title
plt.title("CPU resources usage distribution")

# Add labels to the axes
plt.ylim(0,105)
plt.xlabel("Orchestration Solutions")
plt.ylabel("CPU usage over time (%)")
plt.show()

	# # Convertir le timestamp en objet datetime
	# data['Timestamp'] = pd.to_datetime(data['Timestamp'])

	# # Trouver le timestamp initial (T0)
	# start_time = data['Timestamp'].min()

	# # Calculer le temps écoulé depuis T0 en secondes
	# data['TimeElapsed'] = (data['Timestamp'] - start_time).dt.total_seconds()
	# stat_data = pd.DataFrame()
	# stat_data['CPU'] = data.groupby('TimeElapsed').agg({'CPU': ['min', 'max', 'mean']})
	# # stat_data.columns = ['min', 'max', 'mean']  # Renommer les colonnes pour plus de clarté
	# stat_data['RAM'] = data.groupby('TimeElapsed').agg({'RAM': ['min', 'max', 'mean']})
	# # stat_data.columns = ['min', 'max', 'mean']  # Renommer les colonnes pour plus de clarté
	# stat_data['Storage'] = data.groupby('TimeElapsed').agg({'Storage': ['min', 'max', 'mean']})
	# # stat_data.columns = ['min', 'max', 'mean']  # Renommer les colonnes pour plus de clarté
	# debug(stat_data)