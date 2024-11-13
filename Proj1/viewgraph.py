import networkx as nx
import matplotlib.pyplot as plt
import os

# Load the .gml file
gml_file_path_posts = ''
i=int(input("Enter 1 for post_graph.gml and 2 for user_graph.gml"))
if i==1:
    gml_file_path_posts = os.path.expanduser('~/Desktop/CSE472/Proj1/post_graph.gml')
else:
    gml_file_path_posts = os.path.expanduser('~/Desktop/CSE472/Proj1/user_graph.gml')
G_post = nx.read_gml(gml_file_path_posts)

# Visualize the graph
plt.figure(figsize=(10, 10))
nx.draw(G_post, with_labels=True, node_size=500, node_color='lightblue', font_size=10, font_weight='bold')
plt.show()
