import networkx as nx
from pyvis.network import Network
import random, os

# Load the GraphML file

base_path = '/home/fzm/Desktop/LightRAG/_index_hongloumeng_qwenapi'

G = nx.read_graphml(os.path.join(base_path,'graph_chunk_entity_relation.graphml'))

# Create a Pyvis network
net = Network(height="100vh", notebook=True)

# Convert NetworkX graph to Pyvis network
net.from_nx(G)


# Add colors and title to nodes
for node in net.nodes:
    node["color"] = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    if "description" in node:
        node["title"] = node["description"]

# Add title to edges
for edge in net.edges:
    if "description" in edge:
        edge["title"] = edge["description"]

# Save and display the network
net.show(os.path.join(base_path,"knowledge_graph.html"))
