def get_id_text_mapping(graph):
    ids_to_text = {}
    for node in graph["nodes"]:
        node_id = node["id"]
        text = node["text"]
        ids_to_text[node_id] = text
    return ids_to_text

def translate_edges(graph, text_to_ids):
    translated_edges = set()
    for edge in graph["edges"]:
        source = edge["source"]
        target = edge["target"]
        label = edge["label"]
        translated_edges.add((text_to_ids[source], text_to_ids[target], label))

def check_isomorphism(graph1, graph2):
    ids_to_text1 = get_id_text_mapping(graph1)
    ids_to_text2 = get_id_text_mapping(graph2)
    
    g1_nodes = set(ids_to_text1.values())
    g2_nodes = set(ids_to_text2.values())
    if g1_nodes != g2_nodes:
        print("nodes different")
        return False

    translated_edges1 = translate_edges(graph1, ids_to_text1)
    translated_edges2 = translate_edges(graph2, ids_to_text2)

    if translated_edges1 != translated_edges2:
        print("edges different")
        return False
    
    return True