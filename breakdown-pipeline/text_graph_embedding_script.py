import json
import os


def create_edgeDict(json_data):
    new_data = json.loads(json_data_new)
    edge_dict = {}
    for edge in new_data['edges']:
        curr_source = edge['source']
        curr_target = edge['target']
        curr_relations = edge['label']
        curr_source += 1
        curr_target += 1
        source_id = 'N' + str(curr_source)
        target_id = 'N' + str(curr_target)
        if source_id not in edge_dict:
            edge_dict[source_id] = []

        edge_dict[source_id].append((curr_relations, target_id))
    
    return edge_dict


def embed_graph_into_text(essay, json_data, edges_dict):
    
    data = json.loads(json_data)
    
    for node in data['nodes']:
        node_text = node['text']
        node_num = node['id'][1:]
        node_id = 'N' + str(node_num)
        relations = ''
        if node_id in edges_dict:
            value = edges_dict.get(node_id)
            if len(value) > 1:
                relations = ' and '.join([str(relation[0]) + ' ' + str(relation[1]) for relation in value])
            else:
                relations = str(value[0][0]) + ' ' + str(value[0][1])  
        start_index = essay.find(node_text)
        if start_index != -1:
            #Get ending index, now start and end position found
            end_index = start_index + len(node_text)
            new_text = f"[{node_text} | {node_id}]"
            if (len(relations) == 0):
                essay = essay[:start_index] + new_text + essay[end_index:]
            else:
                essay = essay[:start_index] + new_text + ' (' + relations + ')' + essay[end_index:]        
    return essay  

#Usage: ((embed_graph_into_text(original_essay, json_for_essay, create_edgeDict(json_for_essay))))