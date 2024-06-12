echo $'******Generating results for nodes resource usage******\n'
python3 nodes_plotter.py

printf $'\n******Generating results for pods duration******\n'

python3 pods_plotter.py

echo $'\n******Generating results for pods displacement******\n'
python3 nodes_displacement.py
