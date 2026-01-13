import networkx as nx

G = nx.read_graphml("/workspace/lightrag/dickens/HLM/graph_chunk_entity_relation.graphml")

print(type(G))          # Graph / DiGraph / MultiDiGraph
print(G.number_of_nodes())
print(G.number_of_edges())

# 看几个实体
list(G.nodes(data=True))[:5]

# 看几个关系
list(G.edges(data=True))[:5]



import matplotlib.pyplot as plt

nx.draw(G, with_labels=True, node_size=300)
plt.show()