import json
import graphviz
import glob

user = "Vasanth"
fpath = "practice/" + user + "/JSON/*"

for file in glob.glob(fpath):
    with open(file, 'r') as f:
        # Load the JSON data
        graph_data = json.loads(f.read())

        # Create a Graphviz Digraph
        dot = graphviz.Digraph()

        # Add nodes to the Digraph
        for node in graph_data['nodes']:
            dot.node(node["id"], label=node["text"])

        # Add edges to the Digraph
        for edge in graph_data['edges']:
            dot.edge(edge["source"], edge["target"], label=edge["label"])

        # Render the graph to a file
        dot.render(user + file.split('/')[-1].split('.')[0], format='png', cleanup=True)