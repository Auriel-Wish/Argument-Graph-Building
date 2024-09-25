import json

def is_valid_graph(graph: dict) -> bool:
    try:
        nodes = graph['nodes']
        edges = graph['edges']
        node_ids = set()

        if len(nodes) == 0:
            return False
        for node in nodes:
            if 'text' not in node or 'id' not in node:
                print("text or id not in node")
                return False
            curr_id = node['id']
            if any(key not in ['id', 'text', 'type', 'score'] for key in node.keys()):
                print(curr_id, "invalid key")
                return False
            if not isinstance(node['text'], str) or ('score' in node and not (isinstance(node['score'], int) or isinstance(node['score'], float))):
                print(curr_id, "invalid type for field(s)")
                return False
            if curr_id in node_ids:
                print(curr_id, "repeated node id")
                return False
            if not is_valid_node_id(curr_id):
                print(curr_id, "invalid node id")
                return False
            node_ids.add(curr_id)
        for edge in edges:
            if 'label' not in edge or 'source' not in edge or 'target' not in edge:
                print("edge label, source, or target not in edge")
                return False
            label = edge['label']
            source = edge['source']
            target = edge['target']
            if any(key not in ['label', 'source', 'target'] for key in edge.keys()):
                print(source, target, "invalid field in edge")
                return False
            if not is_valid_node_id(edge['source']) or not is_valid_node_id(edge['target']):
                print(source, target, "invalid node id")
                return False
            if not is_valid_edge_label(edge['label']):
                print(source, target, "invalid relation")
                return False
            if edge['source'] not in node_ids or edge['target'] not in node_ids:
                print(source, target, "source and/or target not in nodes")
                return False
        return True
    except:
        return False

def is_valid_node_id(node_id: str) -> bool:
    return isinstance(node_id, str) and (node_id.startswith("N") or node_id.startswith("E")) and node_id[1:].isnumeric()

def is_valid_edge_label(edge_label: str) -> bool:
    return edge_label in ["support", "attack"]

def read_json_file(file_path: str) -> dict:
    with open(file_path, 'r') as f:
        return json.load(f)